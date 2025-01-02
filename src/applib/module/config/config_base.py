import os
import json
import shutil
import tomlkit
import tomlkit.exceptions
import traceback
from pathlib import Path
from numbers import Number
from typing import Any, Callable, Literal, Mapping, Optional
from time import time
from pydantic import ValidationError

from ...app.common.core_signalbus import core_signalbus

from .tools.ini_file_parser import IniFileParser
from ..exceptions import IniParseError, InvalidMasterKeyError, MissingFieldError
from .internal.core_args import CoreArgs
from .tools.config_tools import writeConfig
from ..logging import logger
from ..tools.types.general import Model, StrPath
from ..tools.utilities import formatValidationError, insertDictValue, retrieveDictValue


class ConfigBase:
    """Base class for all configs"""

    _logger = logger

    def __init__(
        self,
        template_model: dict,
        validation_model: Model,
        config_name: str,
        config_path: StrPath,
        save_interval: Number = 1,
    ) -> None:
        """
        Base class for all configs.

        Parameters
        ----------
        template_model : dict
            A dict created from a `Model`, resembling a template,
            from which the config will be created.

        validation_model : Model
            The Pydantic model used to validate the config.

        config_name : str
            The name of the config to create.

        config_path : StrPath
            The config's location on disk.

        save_interval : Number, optional
            Time between config saves in seconds.
            By default `1`.
        """
        self._load_failure = False  # The config failed to load
        self._is_modified = False  # A modified config needs to be written to disk
        self._save_interval = save_interval  # Time between config saves in seconds

        # Prevent excessive disk writing (with multiple write requests in a short time span)
        self._last_save_time = time()

        self._config_name = config_name
        self._config_path = config_path
        self._template_model = template_model
        self._validation_model = validation_model
        self._connectSignalToSlot()

        # Initialize config after everything's set up
        self._config = self._initConfig()

    def _connectSignalToSlot(self) -> None:
        core_signalbus.configNameUpdated.connect(self._onConfigNameUpdated)
        core_signalbus.doSaveConfig.connect(self._onSaveConfig)

    def _onConfigNameUpdated(self, old_name: str, new_name: str) -> None:
        if old_name == self._config_name:
            self._config_name = new_name

    def _onSaveConfig(self, config_name: str) -> None:
        if self._config_name == config_name:
            self.saveConfig()

    def _checkMissingFields(self, config: dict, template_model: dict, error_prefix: str = "") -> None:
        """
        Compare the config against the template_model for missing
        sections/settings and vice versa.

        Parameters
        ----------
        config : dict
            The config loaded from a file.

        template_model : dict
            The template_model associated with `config`.

        error_prefix : str
            Prefix error messages with this string.
            By default `""`.

        Raises
        ------
        MissingFieldError
            If any missing or unknown sections/settings are found.
        """
        all_errors, section_errors, field_errors = [], [], []
        parents = []

        def searchFields(
            config: dict,
            template_model: dict,
            search_mode: Literal["missing", "unknown"],
        ) -> None:
            """
            Helper function to keep track of parents while traversing.
            Use `search_mode` to select which type of field to search for.

            Parameters
            ----------
            config : dict
                The config loaded from a file.

            template_model : dict
                The template_model associated with `config`.

            search_mode : Literal["missing", "unknown"]
                Specify which type of field to search for.
            """
            # The dict to search depth-first in. Should be opposite of validation dict
            search_dict = template_model if search_mode == "missing" else config
            # The dict to compare the search dict against. Should be opposite of search dict
            validation_dict = config if search_mode == "missing" else template_model
            for key, value in search_dict.items():
                # The template_model is still nested (dict key/value pairs, i.e., sections)
                if isinstance(value, dict):
                    if key in validation_dict:  # section exists
                        parents.append(key)
                        next_search = (
                            (config[key], value)
                            if search_mode == "missing"
                            else (value, template_model[key])
                        )
                        searchFields(*next_search, search_mode=search_mode)
                    else:
                        section_errors.append(
                            f"{search_mode.capitalize()} {f"subsection '{".".join(parents)}.{key}'" if parents else f"section '{key}'"}"
                        )
                # We've reached the bottom of the nesting (non-dict key/value pairs)
                elif key not in validation_dict:
                    if parents:
                        field_errors.append(
                            f"{search_mode.capitalize()} setting '{key}' in {f"section '{parents[0]}'" if len(parents) == 1 else f"subsection '{".".join(parents)}'"}"
                        )
                    else:
                        field_errors.append(
                            f"{search_mode.capitalize()} setting '{key}'"
                        )
            else:
                if parents:
                    parents.pop()

        searchFields(config, template_model, search_mode="missing")
        searchFields(config, template_model, search_mode="unknown")

        # Ensure all section errors are displayed first
        all_errors.extend(section_errors)
        all_errors.extend(field_errors)
        if len(all_errors) > 0:
            if error_prefix:
                all_errors = [f"{error_prefix}: {error}" for error in all_errors]
            raise MissingFieldError(all_errors)

    def _initConfig(self) -> dict:
        """
        Loads the config from a file.

        This is the default implementation.
        To change its behavior, simply @override this method in a subclass.

        Returns
        -------
        dict[str, Any]
            The loaded config.
        """
        config, self._load_failure = self._loadConfig(
            validator=self._validateLoad,
            template_model=self._template_model,
        )
        return config

    def _validateLoad(self, raw_config: Mapping) -> dict:
        """
        Validates the config when loaded from a file.

        This is the default implementation.
        To change its behavior, simply @override this method in a subclass.

        Parameters
        ----------
        raw_config : dict
            The raw, unvalidated config loaded from a file.

        Returns
        -------
        dict[str, Any]
            The validated config.
        """
        validated_config = self._validation_model.model_validate(raw_config)
        config = validated_config.model_dump()
        self._checkMissingFields(raw_config, config)
        return config

    def _validate(self, config: dict) -> None:
        """
        Validates the config when a value is changed,
        ensuring only valid values exists at any given time.

        This is the default implementation.
        To change its behavior, simply @override this method in a subclass.

        Parameters
        ----------
        config : dict
            The config to validate.
        """
        self._config = self._validation_model.model_validate(config).model_dump()

    def _validateValue(
        self,
        key: str,
        value: Any,
        validator: Callable[[dict], dict],
        parent_key: Optional[str] = None,
    ) -> tuple[bool, bool]:
        """
        Insert and validate a value in `config`.

        Parameters
        ----------
        key : str
            The key to search for.

        value : Any
            The value to insert. Maps to `key`.

        validator : Callable[[dict], dict]
            The validator callable that validates `config`.

        parent_key : str | None, optional
            Search for `key` within the scope of a parent key.

        Returns
        -------
        tuple[bool, bool]
            Returns a tuple of values:
            * [0]: True if an error occured.
            * [1]: False if a validation error occurred.
        """
        is_error, is_valid = False, True
        msg_prefix = f"Config '{self._config_name}':"
        try:
            old_value = insertDictValue(self._config, key, value, parent_key=parent_key)
            validator(self._config, self._config_name)
        except KeyError as err:
            is_error = True
            logger.error(err.args[0])
        except ValidationError as err:
            is_error, is_valid = True, False
            insertDictValue(
                self._config, key, old_value, parent_key=parent_key
            )  # Restore value
            logger.warning(
                f"{msg_prefix} Unable to validate value '{value}' for setting '{key}': "
                + formatValidationError(err)
            )
        except Exception:
            is_error = True
            logger.error(
                f"{msg_prefix} An unexpected error occurred while validating value '{value}' using key '{key}'\n"
                + traceback.format_exc(limit=CoreArgs.traceback_limit)
            )
        finally:
            return is_error, is_valid

    def _loadConfig(
        self,
        validator: Optional[Callable[[Mapping], dict]] = None,
        template_model: Optional[dict] = None,
        do_write_config: bool = True,
        use_validator_on_error: bool = True,
        retries: int = 1,
    ) -> tuple[dict | None, bool]:
        """
        Read and validate the config file residing at the supplied config path.

        Parameters
        ----------
        validator : Callable[[Mapping], dict]
            A callable that validates the config.
            Must take the raw config as input and return a dict of the validated config.

        template_model : dict | None, optional
            A validated config created by the supplied validation model.
            NOTE: Must be supplied if `do_write_config` is True.
            By default `None`.

        do_write_config : bool, optional
            Manipulate with files on the file system to recover from soft errors.
            By default True.

        use_validator_on_error : bool, optional
            Use the validator function for the next config reload,
            if the current config failed to load due to a validation error.

        retries : int, optional
            Reload the config X times if soft errors occur.
            Note: This has no effect if `do_write_config` is False.
            By default 1.

        Returns
        -------
        tuple[dict | None, bool]
            Returns a tuple of values:
            * [0]: The config file converted to a dict.
            * [1]: True if the config failed to load.

        Raises
        ------
        NotImplementedError
            The file at the config path is not a supported format.
        """
        is_error, failure, reload_failure = False, False, False
        can_reload = do_write_config or not use_validator_on_error
        config = None
        msg_prefix = f"{self._config_name}:"
        filename = os.path.split(self._config_path)[1]
        extension = os.path.splitext(filename)[1].strip(".")
        try:
            with open(self._config_path, "rb") as file:
                if extension.lower() == "toml":
                    raw_config = tomlkit.load(file)
                elif extension.lower() == "ini":
                    raw_config = IniFileParser.load(file)
                elif extension.lower() == "json":
                    raw_config = json.load(file)
                else:
                    err_msg = f"{msg_prefix} Cannot load unsupported file '{self._config_path}'"
                    raise NotImplementedError(err_msg)

            if validator:
                config = validator(raw_config)
            else:
                config = raw_config
        except ValidationError as err:
            is_error, is_recoverable = True, True
            logger.warning(f"{msg_prefix} Could not validate '{filename}'")
            logger.debug(formatValidationError(err))
            if do_write_config:
                self.backupConfig()
                writeConfig(template_model, self._config_path)
        except MissingFieldError as err:
            is_error, is_recoverable = True, True
            err_msg = f"{msg_prefix} Detected incorrect fields in '{filename}':\n"
            for item in err.args[0]:
                err_msg += f"  {item}\n"
            logger.warning(err_msg)
            if do_write_config:
                logger.info(f"{msg_prefix} Repairing config")
                repairedConfig = self._repairConfig(raw_config)
                self.backupConfig()
                writeConfig(repairedConfig, self._config_path)
        except (InvalidMasterKeyError, AssertionError) as err:
            is_error, is_recoverable = True, True
            logger.warning(f"{msg_prefix} {err.args[0]}")
            if do_write_config:
                self.backupConfig()
                writeConfig(template_model, self._config_path)
        # TODO: Add separate except with JSONDecodeError
        except (tomlkit.exceptions.ParseError, IniParseError) as err:
            is_error, is_recoverable = True, True
            logger.warning(
                f"{msg_prefix} Failed to parse '{filename}':\n  {err.args[0]}\n"
            )
            if do_write_config:
                self.backupConfig()
                writeConfig(template_model, self._config_path)
        except FileNotFoundError:
            is_error, is_recoverable = True, True
            logger.info(f"{msg_prefix} Creating '{filename}'")
            if do_write_config:
                writeConfig(template_model, self._config_path)
        except Exception:
            is_error, is_recoverable = True, False
            logger.error(
                f"{msg_prefix} An unexpected error occurred while loading '{filename}'\n"
                + traceback.format_exc(limit=CoreArgs.traceback_limit)
            )
        finally:
            if is_error:
                if can_reload and retries > 0 and is_recoverable:
                    reload_msg = f"{msg_prefix} Reloading '{filename}'"
                    if not use_validator_on_error:
                        reload_msg += " with compatibility mode"
                    logger.info(reload_msg)
                    config, reload_failure = self._loadConfig(
                        validator=validator if use_validator_on_error else None,
                        template_model=template_model,
                        do_write_config=do_write_config,
                        retries=retries - 1,
                    )
                    if not use_validator_on_error:
                        failure = True
                else:
                    failure = True
                    load_failure_msg = f"{msg_prefix} Failed to load '{filename}'"
                    if template_model:
                        load_failure_msg += ". Loading template as config"
                        config = template_model  # Use the template_model as config if all else fails
                        logger.warning(load_failure_msg)
                    else:
                        logger.error(load_failure_msg)
            else:
                logger.info(f"{msg_prefix} Config '{filename}' loaded!")
            return config, failure or reload_failure

    def _repairConfig(self, config: dict) -> dict:
        """
        Preserve all valid values in `config` when some of its fields are determined invalid.
        Fields are taken from the `config`'s associated template_model if they could not be preserved.

        Parameters
        ----------
        config : dict
            The config loaded from a file.

        Returns
        -------
        dict
            A new config where all values are valid with as many as possible
            preserved from `config`.
        """
        repaired_config = {}
        for template_key, value in self._template_model.items():
            if isinstance(value, dict) and template_key in config:
                # Search config/template_model recursively, depth-first
                repaired_config |= {
                    template_key: self._repairConfig(config[template_key], value)
                }
            elif template_key in config:
                # Preserve value from config
                repaired_config |= {template_key: config[template_key]}
            else:
                # Use value from template_model
                repaired_config |= {template_key: value}
        return repaired_config

    def setTemplateModel(self, template_model: dict) -> None:
        """
        Set a `template_model` for this config.

        Parameters
        ----------
        template_model : dict
            A dict created from a `Model`, resembling a template,
            from which the config will be created.
        """
        self._template_model = template_model

    def setValidationModel(self, validation_model: Model) -> None:
        """
        Set a `validation_model` for this config.

        Parameters
        ----------
        validation_model : Model
            The Pydantic model used to validate the config.
        """
        self._validation_model = validation_model

    def getConfig(self) -> dict:
        """
        Get the config's underlying dict.

        Returns
        -------
        dict[str, dict]
            The config's underlying dict.
        """
        return self._config

    def getConfigName(self) -> str:
        return self._config_name

    def getFailureStatus(self) -> bool:
        """
        Whether the config failed to load.

        Returns
        -------
        bool
            True == failed (i.e. the config is not usable).
        """
        return self._load_failure

    def setFailureStatus(self, status: bool) -> None:
        self._load_failure = status

    def getValue(
        self,
        key: str,
        parent_key: Optional[str] = None,
        default: Any = None,
        use_template_model: bool = False,
    ) -> Any:
        """
        Get a value from the config's underlying dict.
        Return first value found. If there is no item with that key, return default.

        This is the default implementation.
        To change its behavior, simply @override this method in a subclass.

        NOTE: the dictionary is usually nested. Thus, the "get" method of a Python dict
        is insufficient to retrieve all values.

        Parameters
        ----------
        key : str
            The key to search for.

        parent_key : str, optional
            Search for `key` within the scope of a parent key.

        default : Any, optional
            Fallback value if `key` is not found.
            By default `None`.

        use_template_model : bool, optional
            Search for `key` in the configs associated use_template_model.
            This useful for getting e.g. default values of settings.
            By default False.

        Returns
        -------
        Any
            The value of `key`, if found, else `default`.
        """
        config = self._template_model if use_template_model else self._config
        value = retrieveDictValue(
            d=config, key=key, parent_key=parent_key, default=default
        )
        if value is None:
            self._logger.warning(
                f"Config '{self._config_name}': Could not find key '{key}' in the config. Returning default: '{default}'"
            )
        return value

    def setValue(self, key: str, value: Any, parent_key: Optional[str] = None) -> bool:
        """
        Assign `value` to `key` in the config's underlying dict, overwriting any previous value.

        Parameters
        ----------
        key : str
            The key to search for.

        value : Any
            The value to insert. Maps to `key`.

        parent_key : str, optional
            Search for `key` within the scope of a parent key.

        Returns
        -------
        bool
            Whether the config was validated successfully after `value` was inserted.
            True == invalid (i.e. the value was NOT saved).
        """
        is_error, is_invalid = self._validateValue(
            key=key,
            value=value,
            validator=self._validate,
            parent_key=parent_key,
        )
        if is_error:
            core_signalbus.configStateChange.emit(False, "Failed to save setting", "")
        else:
            core_signalbus.configUpdated.emit(self._config_name, key, (value,))
            self._is_modified = True
        return is_invalid

    def saveConfig(self) -> None:
        """Write config to disk"""
        try:
            if (
                self._is_modified
                and (self._last_save_time + self._save_interval) < time()
            ):
                self._last_save_time = time()
                writeConfig(self._config, self._config_path)
                self._is_modified = False
        except Exception:
            msg = "Failed to save the config"
            self._logger.error(
                f"Config '{self._config_name}': {msg}\n"
                + traceback.format_exc(limit=CoreArgs.traceback_limit)
            )
            core_signalbus.configStateChange.emit(False, msg, "")

    def backupConfig(self) -> None:
        """Creates a backup of the config file on disk, overwriting any existing backup."""
        try:
            file = os.path.split(self._config_path)[1]
            backup_file = Path(f"{self._config_path}.bak")
            logger.debug(f"Creating backup of '{file}' to '{backup_file}'")
            shutil.copyfile(self._config_path, backup_file)
        except Exception:
            logger.error(
                f"Failed to create backup of '{self._config_path}'\n"
                + traceback.format_exc(limit=CoreArgs.traceback_limit)
            )
