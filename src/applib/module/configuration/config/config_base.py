import json
import os
import shutil
import traceback
from numbers import Number
from pathlib import Path
from time import time
from typing import Any, Callable, Iterable, Literal, Mapping, Optional, Union, override

import tomlkit
import tomlkit.exceptions
from pydantic import ValidationError

from ....app.common.core_signalbus import core_signalbus
from ...datastructures.redblacktree_mapping import _rbtm_item
from ...exceptions import IniParseError, InvalidMasterKeyError, MissingFieldError
from ...tools.types.general import Model, StrPath
from ...tools.types.templates import AnyTemplate
from ...tools.utilities import format_validation_error
from ..internal.core_args import CoreArgs
from ..mapping_base import MappingBase
from ..tools.config_tools import ConfigUtils
from ..tools.config_utils.config_enums import ConfigLoadOptions
from ..tools.ini_file_parser import IniFileParser


class ConfigBase(MappingBase):
    def __init__(
        self,
        name: str,
        template: AnyTemplate,
        validation_model: Model | None,
        file_path: StrPath,
        save_interval: Number = 1,
    ) -> None:
        """
        Base class for all configs.

        Parameters
        ----------
        name : str
            The name of the config to create.

        template : AnyTemplate
            The template used to create `validation_model`.

        validation_model : Model | None
            The Pydantic model used to validate the config.

        file_path : StrPath
            The config's location on disk.

        save_interval : Number, optional
            Time between config saves in seconds.
            By default 1.
        """
        self._is_modified = False  # A modified config needs to be written to disk
        self._save_interval = save_interval  # Time between config saves in seconds
        self._last_save_time = time()  # Prevent excessive disk writing
        self.template = template
        self.validation_model = (
            validation_model.model_construct() if validation_model else validation_model
        )
        self.name = name
        self.file_path = file_path
        self.failure = False  # The config failed to load
        self.__connectSignalToSlot()

        # Initialize config after everything is set up
        super().__init__([self._init_config()], name)

    def __connectSignalToSlot(self) -> None:
        core_signalbus.configNameUpdated.connect(self._onConfigNameUpdated)

    def _onConfigNameUpdated(self, old_name: str, new_name: str) -> None:
        if old_name == self.name:
            self.name = new_name

    @override
    def _is_setting(self, item: _rbtm_item) -> bool:
        check = False
        k, v, pos, ps = item
        try:
            check = not isinstance(v, dict)
            check = check or not isinstance(v.x[0][0], dict)
        except Exception:
            pass
        return check

    @override
    def _prefix_msg(self) -> str:
        return f"Config '{self.name}':"

    def _check_missing_fields(
        self, config: dict, model_dict: dict, error_prefix: str = ""
    ) -> None:
        """
        Compare the config against the model_dict for missing
        sections/settings and vice versa.

        Parameters
        ----------
        config : dict
            The config loaded from a file.

        model_dict : dict
            The model_dict associated with `config`.

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
            config: dict,
            model_dict: dict,
            search_mode: Literal["missing", "unknown"],
        ) -> None:
            """
            Helper function to keep track of parents while traversing.
            Use `search_mode` to select which type of field to search for.

            Parameters
            ----------
            config : dict
                The config loaded from a file.

            model_dict : dict
                The model_dict associated with `config`.

            search_mode : Literal["missing", "unknown"]
                Specify which type of field to search for.
            """
            # The dict to search depth-first in. Should be opposite of validation dict
            search_dict = model_dict if search_mode == "missing" else config
            # The dict to compare the search dict against. Should be opposite of search dict
            validation_dict = config if search_mode == "missing" else model_dict
            for key, value in search_dict.items():
                # The model_dict is still nested (dict key/value pairs, i.e., sections)
                if isinstance(value, dict):
                    if key in validation_dict:  # section exists
                        parents.append(key)
                        next_search = (
                            (config[key], value)
                            if search_mode == "missing"
                            else (value, model_dict[key])
                        )
                        search_fields(*next_search, search_mode=search_mode)
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

        search_fields(config, model_dict, search_mode="missing")
        search_fields(config, model_dict, search_mode="unknown")

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
            model_dict=self.validation_model.model_dump(),
        )
        return config

    def _validate_load(self, raw_config: Mapping) -> dict:
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
        config = self.validation_model.model_validate(raw_config).model_dump()
        self._check_missing_fields(raw_config, config)
        return config

    def _validate(self, config: dict) -> None:
        """
        Validates the config when a value is changed,
        ensuring only valid values exists at any given time.

        Parameters
        ----------
        config : dict
            The config to validate.
        """
        self.add_mapping(self.validation_model.model_validate(config).model_dump())

    def _validation_wrapper(
        self,
        key: str,
        value: Any,
        validator: Callable[[dict], None],
        parents: Union[str, list[str]] = [],
        search_mode: Literal["strict", "smart", "immediate", "any"] = "smart",
    ) -> bool:
        """
        Insert and validate a value in the config.

        Parameters
        ----------
        key : str
            The key to search for.

        value : Any
            The value to insert. Maps to `key`.

        validator : Callable[[dict], None]
            The validator callable that validates the config.

        parents : str | list[str], optional
            The parents of `key`. Used for lookup in the config.

        Returns
        -------
        bool
            True if an error occured.
        """
        is_error, is_missing_key = False, False
        try:
            try:
                old_value = super().get_value(
                    key=key, parents=parents, search_mode=search_mode, errors="raise"
                )
            except (KeyError, LookupError):
                is_missing_key = True
            super().set_value(
                key=key, value=value, parents=parents, search_mode=search_mode
            )
            validator(self.dump())
        except ValidationError as err:
            is_error = True
            self._logger.warning(
                f"{self._prefix_msg()} Unable to validate value '{value}' for key '{key}': "
                + format_validation_error(err)
            )
            if not is_missing_key:
                super().set_value(
                    key=key, value=old_value, parents=parents, search_mode=search_mode
                )
        except Exception:
            is_error = True
            self._logger.error(
                f"{self._prefix_msg()} An unexpected error occurred while validating value '{value}' using key '{key}'\n"
                + traceback.format_exc(limit=CoreArgs._core_traceback_limit)
            )
        finally:
            if is_error:
                core_signalbus.configStateChange.emit(
                    False, "Failed to save setting", ""
                )
            else:
                core_signalbus.configUpdated.emit(
                    (self.name, self.template.name), key, (value,), parents
                )
                self._is_modified = True
            return is_error

    def _load_config(
        self,
        validator: Optional[Callable[[Mapping], dict]] = None,
        model_dict: Optional[dict] = None,
        load_options: (
            ConfigLoadOptions | list[ConfigLoadOptions]
        ) = ConfigLoadOptions.WRITE_CONFIG,
        retries: int = 1,
    ) -> tuple[dict | None, bool]:
        """
        Read and validate the config file residing at the supplied config path.

        Parameters
        ----------
        validator : Callable[[Mapping], dict]
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
        config = None
        filename = os.path.split(self.file_path)[1]
        extension = os.path.splitext(filename)[1].strip(".")
        write_config = ConfigLoadOptions.WRITE_CONFIG in load_options
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
                self._logger.info(f"{self._prefix_msg()} Config '{filename}' loaded!")
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
        repaired_config = {}

        def repair(c: dict, md: dict):
            nonlocal repaired_config
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

        repair(config, model_dict)
        return repaired_config

    @override
    def set_value(
        self,
        key: str,
        value: Any,
        parents: Union[str, list[str]] = [],
        search_mode: Literal["strict", "smart", "immediate", "any"] = "smart",
    ) -> bool:
        """
        Assign `value` to `key`.

        Parameters
        ----------
        key : str
            The key to search for.

        value : Any
            The value to insert.

        parents : str | list[str], optional
            The parents of `key`. Used to uniquely identify `key`

        search_mode : Literal["strict", "smart", "immediate", "any"], optional
            How to search for `key`.
                "strict"
                    Requires `parents` to match exactly.
                    I.e. ["a", "b"] == ["a", "b"]
                "smart"
                    Tries to find `key` using different heuristics.
                    Note that it can result in the wrong key under certain conditions.
                "immediate"
                    Requires `parents` to be a Hashable that matches the closest parent.
                    I.e. "b" == ["a", "b"]
                "any"
                    Requires `parents` to be a Hashable that matches any parent.
                    I.e. "a" == ["a", "b"]

            By default "smart".

        Returns
        -------
        bool
            Whether the config was validated successfully after `value` was inserted.
            True == invalid (i.e. the value was NOT saved).
        """
        return self._validation_wrapper(
            key=key,
            value=value,
            validator=self._validate,
            parents=parents,
            search_mode=search_mode,
        )

    def save_config(self) -> None:
        """Write config to disk"""
        try:
            if (
                self._is_modified
                and (self._last_save_time + self._save_interval) < time()
            ):
                self._last_save_time = time()
                ConfigUtils.writeConfig(self.dump(), self.file_path)
                self._is_modified = False
        except Exception:
            msg = "Failed to save the config"
            self._logger.error(
                f"{self._prefix_msg()} {msg}\n"
                + traceback.format_exc(limit=CoreArgs._core_traceback_limit)
            )
            core_signalbus.configStateChange.emit(False, msg, "")

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
                + traceback.format_exc(limit=CoreArgs._core_traceback_limit)
            )
