import json
import os
import shutil
import traceback
from collections.abc import Callable, Mapping
from pathlib import Path
from time import time
from typing import Any, Literal, override

import tomlkit
import tomlkit.exceptions
from pydantic import ValidationError

from ....app.common.core_signalbus import core_signalbus
from ...exceptions import IniParseError, InvalidMasterKeyError, MissingFieldError
from ...logging import LoggingManager
from ...tools.types.general import Model, StrPath
from ...tools.types.templates import AnyTemplate
from ...tools.utilities import format_validation_error
from ..internal.core_args import CoreArgs
from ..mapping_base import MappingBase
from ..tools.config_tools import ConfigUtils
from ..tools.config_utils.config_enums import ConfigLoadOptions
from ..tools.ini_file_parser import IniFileParser
from ..tools.search import SearchMode


class ConfigBase(MappingBase):
    _logger = None

    def __init__(
        self,
        name: str,
        template: AnyTemplate,
        validation_model: type[Model] | None,
        file_path: StrPath,
        save_interval: int = 1,
    ) -> None:
        """Base class for all configs.

        Parameters
        ----------
        name : str
            The name of the config to create.
        template : AnyTemplate
            The template used to create `validation_model`.
        validation_model : type[Model] | None
            The Pydantic model used to validate the config. If None, no validation is performed.
        file_path : StrPath
            The config's location on disk.
        save_interval : int, optional
            Time between config saves in seconds.
            By default 1.
        """
        self._is_modified = False
        """A modified config needs to be written to disk"""
        self._save_interval = save_interval
        """Time between config saves in seconds"""
        self._last_save_time = time()  # Prevent excessive disk writing
        self.template = template
        self.validation_model = (
            validation_model.model_construct() if validation_model else None
        )
        self.name = name
        self.file_path = file_path
        self.failure = False
        """The config failed to load"""
        self.__connectSignalToSlot()

        if self._logger is None:
            # Lazy load the logger
            self._logger = LoggingManager()

        # Initialize config after everything is set up
        super().__init__(self._init_config())

    def __connectSignalToSlot(self) -> None:
        core_signalbus.configNameUpdated.connect(self._onConfigNameUpdated)

    def _onConfigNameUpdated(self, old_name: str, new_name: str) -> None:
        if old_name == self.name:
            self.name = new_name

    def _prefix_msg(self) -> str:
        return f"Config '{self.name}':"

    def _check_missing_fields(
        self, config: Mapping, model: Mapping, error_prefix: str = ""
    ) -> None:
        """
        Compare the config against the model_dict for missing
        sections/settings and vice versa.

        Parameters
        ----------
        config : Mapping
            The config loaded from a file.

        model : Mapping
            The model associated with `config`.

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

        def search_fields(
            config: Mapping,
            model: Mapping,
            search_mode: Literal["missing", "unknown"],
        ) -> None:
            """
            Helper function to keep track of parents while traversing.
            Use `search_mode` to select which type of field to search for.

            Parameters
            ----------
            config : Mapping
                The config loaded from a file.

            model : Mapping
                The model associated with `config`.

            search_mode : Literal["missing", "unknown"]
                Specify which type of field to search for.
            """
            # The mapping to search depth-first in. Should be opposite of validation mapping
            search_dict = model if search_mode == "missing" else config
            # The mapping to compare the search dict against. Should be opposite of search mapping
            validation_dict = config if search_mode == "missing" else model
            for key, value in search_dict.items():
                # The model is still nested (mapping key/value pairs, i.e., sections)
                if isinstance(value, Mapping):
                    if key in validation_dict:  # section exists
                        parents.append(key)
                        next_search = (
                            (config[key], value)
                            if search_mode == "missing"
                            else (value, model[key])
                        )
                        search_fields(*next_search, search_mode=search_mode)
                    else:
                        section_errors.append(
                            f"{search_mode.capitalize()} {f"subsection '{".".join(parents)}.{key}'" if parents else f"section '{key}'"}"
                        )
                # We've reached the bottom of the nesting (non-mapping key/value pairs)
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

        search_fields(config, model, search_mode="missing")
        search_fields(config, model, search_mode="unknown")

        # Ensure all section errors are displayed first
        all_errors.extend(section_errors)
        all_errors.extend(field_errors)
        if len(all_errors) > 0:
            if error_prefix:
                all_errors = [f"{error_prefix}: {error}" for error in all_errors]
            raise MissingFieldError(all_errors)

    def _init_config(self) -> dict:
        """Loads the config from a file."""
        config, self.failure = self._load_config(
            validator=self._validate_load,
            model_dict=(
                self.validation_model.model_dump() if self.validation_model else None
            ),
        )
        return config

    def _validate_load(self, raw_config: dict) -> dict:
        """
        Validates the config when loaded from a file.

        Parameters
        ----------
        raw_config : dict
            The raw, unvalidated config loaded from a file.

        Returns
        -------
        dict
            The validated config.
        """
        if self.validation_model:
            config = self.validation_model.model_validate(raw_config).model_dump()
            self._check_missing_fields(raw_config, config)
            return config
        return raw_config

    def _load_config(
        self,
        validator: Callable[[dict], dict] | None = None,
        model_dict: dict | None = None,
        load_options: (
            ConfigLoadOptions | list[ConfigLoadOptions]
        ) = ConfigLoadOptions.WRITE_CONFIG,
        retries: int = 1,
    ) -> tuple[dict, bool]:
        """
        Read and validate the config file residing at the supplied config path.

        Parameters
        ----------
        validator : Callable[[dict], dict]
            A callable that validates the config.
            Must take the raw config as input and return a dict of the validated config.

        model_dict : dict | None, optional
            A validated config created by the supplied validation model.
            NOTE: Must be supplied if `load_options` contains ConfigLoadOptions.WRITE_CONFIG.
            By default None.

        load_options : ConfigLoadOptions | list[ConfigLoadOptions], optional
            Manipulate with files on the file system to recover from soft errors.
            By default ConfigLoadOptions.WRITE_CONFIG.

        retries : int, optional
            Reload the config X times if soft errors occur.
            Note: This has no effect if `load_options` does not contain ConfigLoadOptions.WRITE_CONFIG.
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
        if not isinstance(load_options, list):
            load_options = [load_options]

        is_error, failure = False, False
        config = {}
        filename = os.path.split(self.file_path)[1]
        extension = os.path.splitext(filename)[1].strip(".")
        write_config = ConfigLoadOptions.WRITE_CONFIG in load_options

        if write_config and model_dict is None:
            self._logger.warning(
                f"{self._prefix_msg()} Cannot write config. {type(model_dict)} is not a valid model"
            )
            write_config = False

        try:
            with open(self.file_path, "rb") as file:
                if extension.lower() == "toml":
                    raw_config = tomlkit.load(file)
                elif extension.lower() == "ini":
                    raw_config = IniFileParser.load(file)
                elif extension.lower() == "json":
                    raw_config = json.load(file)
                else:
                    err_msg = f"{self._prefix_msg()} Cannot load unsupported file '{self.file_path}'"
                    raise NotImplementedError(err_msg)

            if ConfigLoadOptions.IGNORE_VALIDATION_ERROR in load_options:
                config = raw_config

            if validator:
                config = validator(raw_config)
        except ValidationError as err:
            is_error, is_recoverable = True, True
            self._logger.warning(
                f"{self._prefix_msg()} Could not validate '{filename}'"
            )
            self._logger.debug(format_validation_error(err))
            if write_config:
                self.backup_config()
                ConfigUtils.writeConfig(model_dict, self.file_path)
        except MissingFieldError as err:
            is_error, is_recoverable = True, True
            err_msg = (
                f"{self._prefix_msg()} Detected incorrect fields in '{filename}':\n"
            )
            for item in err.args[0]:
                err_msg += f"  {item}\n"
            self._logger.warning(err_msg)
            if write_config:
                self._logger.info(f"{self._prefix_msg()} Repairing config")
                try:
                    repaired_config = self._repair_config(raw_config, model_dict)
                except Exception:
                    self._logger.error(
                        f"Config repair failed:\n"
                        + traceback.format_exc(limit=CoreArgs._core_traceback_limit)
                    )
                self.backup_config()
                ConfigUtils.writeConfig(repaired_config, self.file_path)
        except (InvalidMasterKeyError, AssertionError) as err:
            is_error, is_recoverable = True, True
            self._logger.warning(f"{self._prefix_msg()} {err.args[0]}")
            if write_config:
                self.backup_config()
                ConfigUtils.writeConfig(model_dict, self.file_path)
        # TODO: Add separate except with JSONDecodeError
        except (tomlkit.exceptions.ParseError, IniParseError) as err:
            is_error, is_recoverable = True, True
            self._logger.warning(
                f"{self._prefix_msg()} Failed to parse '{filename}':\n  {err.args[0]}\n"
            )
            if write_config:
                self.backup_config()
                ConfigUtils.writeConfig(model_dict, self.file_path)
        except FileNotFoundError:
            is_error, is_recoverable = True, True
            self._logger.info(f"{self._prefix_msg()} Creating '{filename}'")
            if write_config:
                ConfigUtils.writeConfig(model_dict, self.file_path)
        except Exception:
            is_error, is_recoverable = True, False
            self._logger.error(
                f"{self._prefix_msg()} An unexpected error occurred while loading '{filename}'\n"
                + traceback.format_exc(limit=CoreArgs._core_traceback_limit)
            )
        finally:
            if is_error:
                if retries > 0 and is_recoverable:
                    reload_msg = f"{self._prefix_msg()} Reloading '{filename}'"
                    self._logger.info(reload_msg)
                    config, failure = self._load_config(
                        validator=validator,
                        model_dict=model_dict,
                        load_options=load_options,
                        retries=retries - 1,
                    )
                else:
                    failure = True
                    load_failure_msg = (
                        f"{self._prefix_msg()} Failed to load '{filename}'"
                    )
                    if model_dict:
                        load_failure_msg += ". Loading template as config"
                        config = (
                            model_dict  # Use the model_dict as config if all else fails
                        )
                        self._logger.warning(load_failure_msg)
                    else:
                        self._logger.error(load_failure_msg)
            else:
                self._logger.info(f"{self._prefix_msg()} '{filename}' loaded!")
            return config, failure

    def _repair_config(self, config: dict, model_dict: dict) -> dict:
        """
        Preserve all valid values in `config` when some of its fields are determined invalid.
        Fields are taken from the `config`'s associated model_dict if they could not be preserved.

        Parameters
        ----------
        config : dict
            The config loaded from a file.

        model_dict : dict
            A validated config created by the supplied validation model.

        Returns
        -------
        dict
            A new config where all values are valid with as many as possible
            preserved from `config`.
        """

        def repair(c: dict, md: dict):
            repaired_config = {}
            for template_key, value in md.items():
                if isinstance(value, dict) and template_key in c:
                    # Search config/model_dict recursively, depth-first
                    repaired_config[template_key] = repair(c[template_key], value)
                elif template_key in c:
                    # Preserve value from config
                    repaired_config[template_key] = c[template_key]
                else:
                    # Use value from model_dict
                    repaired_config[template_key] = value
            return repaired_config

        return repair(config, model_dict)

    @override
    def set_value(
        self,
        key: str,
        value: Any,
        path: str,
        create_missing=False,
    ):
        try:
            old_value = self.get_value(key, path, SearchMode.FUZZY)
            super().set_value(key, value, path, create_missing)
            if self.validation_model:
                self.validation_model.model_validate(self._dict)
        except ValidationError as err:
            is_error = True
            self._logger.warning(
                f"{self._prefix_msg()} Unable to validate value '{value}' for key '{key}': "
                + format_validation_error(err)
            )
            super().set_value(key, old_value, path, False)
        except Exception:
            is_error = True
            self._logger.error(
                f"{self._prefix_msg()} An unexpected error occurred while validating value '{value}' using key '{key}'\n"
                + traceback.format_exc(limit=CoreArgs._core_traceback_limit),
                gui=True,
            )
        finally:
            if not is_error:
                core_signalbus.configUpdated.emit(
                    (self.name, self.template.name), key, (value,), path
                )
                self._is_modified = True
            return is_error

    def save_config(self) -> None:
        """Write config to disk"""
        try:
            if (
                self._is_modified
                and (self._last_save_time + self._save_interval) < time()
            ):
                self._last_save_time = time()
                ConfigUtils.writeConfig(self._dict, self.file_path)
                self._is_modified = False
        except Exception:
            self._logger.error(
                f"{self._prefix_msg()} Failed to save config\n"
                + traceback.format_exc(limit=CoreArgs._core_traceback_limit),
                gui=True,
            )

    def backup_config(self) -> None:
        """Creates a backup of the config file on disk, overwriting any existing backup."""
        try:
            file = os.path.split(self.file_path)[1]
            backup_file = Path(f"{self.file_path}.bak")
            self._logger.debug(f"Creating backup of '{file}' to '{backup_file}'")
            shutil.copyfile(self.file_path, backup_file)
        except Exception:
            self._logger.error(
                f"Failed to create backup of '{self.file_path}'\n"
                + traceback.format_exc(limit=CoreArgs._core_traceback_limit),
                gui=True,
            )
