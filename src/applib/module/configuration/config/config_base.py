import argparse
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
from pydantic import BaseModel, ValidationError

from ....app.common.core_signalbus import core_signalbus
from ...exceptions import IniParseError, InvalidMasterKeyError, MissingFieldError
from ...logging import LoggingManager
from ...tools.types.templates import AnyTemplate
from ...tools.utilities import format_validation_error
from ..internal.core_args import CoreArgs
from ..mapping_base import MappingBase
from ..tools.config_tools import ConfigUtils
from ..tools.config_utils.config_enums import ConfigLoadOptions
from ..tools.ini_file_parser import IniFileParser


class ConfigBase(MappingBase):
    _logger = None

    def __init__(
        self,
        name: str,
        template: AnyTemplate,
        validation_model: type[BaseModel],
        file_path: str | Path,
        save_interval: int = 1,
    ) -> None:
        """Base class for all configs.

        Parameters
        ----------
        name : str
            The name of the config to create.
        template : AnyTemplate
            The template used to create `validation_model`.
        validation_model : type[BaseModel] | None
            The Pydantic model used to validate the config. If None, no validation is performed.
        file_path : str | Path
            The config's location on disk.
        save_interval : int, optional
            Time between config saves in seconds.
            By default 1.
        """
        self._is_modified = False
        self._save_interval = save_interval
        self._last_save_time = time()  # Prevent excessive disk writing
        self.template = template
        self.validation_model = validation_model.model_construct()
        self.name = name
        self.file_path = file_path
        self.failure = False
        self.__connectSignalToSlot()

        if self._logger is None:
            # Lazy load the logger
            self._logger = LoggingManager()

        # Initialize config after everything is set up
        super().__init__(self._init_config(self.file_path))

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
                            f"{search_mode.capitalize()} {f"subsection '{'.'.join(parents)}.{key}'" if parents else f"section '{key}'"}"
                        )
                # We've reached the bottom of the nesting (non-mapping key/value pairs)
                elif key not in validation_dict:
                    if parents:
                        field_errors.append(
                            f"{search_mode.capitalize()} setting '{key}' in {f"section '{parents[0]}'" if len(parents) == 1 else f"subsection '{'.'.join(parents)}'"}"
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

    def update_config(self, data: dict | Mapping | argparse.Namespace | str | Path):
        """Loads the config from `data`."""
        config = self._init_config(data)
        self._rebuild_mapping(config)

    # TODO: https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.extra
    # TODO: https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.validate_assignment
    def _init_config(
        self, data: dict | Mapping | argparse.Namespace | str | Path
    ) -> dict[str, Any]:
        """Loads the config from `data`."""
        config, self.failure = self._load(
            data,
            validator=self._validate_load,
            model_dict=(self.validation_model.model_dump()),
        )
        return config

    def _load(
        self,
        data: dict | Mapping | argparse.Namespace | str | Path,
        validator: Callable[[dict], dict] | None = None,
        model_dict: dict | None = None,
        load_options: (
            ConfigLoadOptions | list[ConfigLoadOptions]
        ) = ConfigLoadOptions.WRITE_CONFIG,
        retries: int = 1,
    ) -> tuple[dict[str, Any], bool]:
        """
        Read and validate `data` as an instance of this config file.

        Parameters
        ----------
        data : str | dict
            The input to load.
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

        write_config = ConfigLoadOptions.WRITE_CONFIG in load_options

        if write_config and model_dict is None:
            self._logger.warning(
                f"{self._prefix_msg()} Cannot write config. {type(model_dict)} is not a valid model"
            )
            write_config = False

        try:
            if isinstance(data, str):
                raw_config = self._load_file(data)
            elif isinstance(data, Path):
                raw_config = self._load_file(f"{data}")
            elif isinstance(data, (dict, Mapping, argparse.Namespace)):
                input_name = f"{type(data).__name__}"
                raw_config = data
            else:
                input_name = data
                not_implemented_msg = (
                    f"{self._prefix_msg()} Cannot load unsupported input '{input_name}'"
                )
                raise NotImplementedError(not_implemented_msg)

            if (
                ConfigLoadOptions.IGNORE_VALIDATION_ERROR in load_options
                or validator is None
            ):
                config = raw_config

            if validator:
                config = validator(raw_config)
        except ValidationError as err:
            is_error, is_recoverable = True, True
            self._logger.warning(
                f"{self._prefix_msg()} Could not validate '{input_name}'"
            )
            self._logger.debug(format_validation_error(err))
            if write_config:
                self.backup_config()
                ConfigUtils.writeConfig(model_dict, self.file_path)
        except MissingFieldError as err:
            is_error, is_recoverable = True, True
            err_msg = (
                f"{self._prefix_msg()} Detected incorrect fields in '{input_name}':\n"
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
                        "Config repair failed:\n"
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
                f"{self._prefix_msg()} Failed to parse '{input_name}':\n  {err.args[0]}\n"
            )
            if write_config:
                self.backup_config()
                ConfigUtils.writeConfig(model_dict, self.file_path)
        except FileNotFoundError:
            is_error, is_recoverable = True, True
            self._logger.info(f"{self._prefix_msg()} Creating '{input_name}'")
            if write_config:
                ConfigUtils.writeConfig(model_dict, self.file_path)
        except Exception:
            is_error, is_recoverable = True, False
            self._logger.error(
                f"{self._prefix_msg()} An unexpected error occurred while loading '{input_name}'\n"
                + traceback.format_exc(limit=CoreArgs._core_traceback_limit)
            )
        finally:
            if is_error:
                if retries > 0 and is_recoverable:
                    reload_msg = f"{self._prefix_msg()} Reloading '{input_name}'"
                    self._logger.info(reload_msg)
                    config, failure = self._load(
                        data=data,
                        validator=validator,
                        model_dict=model_dict,
                        load_options=load_options,
                        retries=retries - 1,
                    )
                else:
                    failure = True
                    load_failure_msg = (
                        f"{self._prefix_msg()} Failed to load '{input_name}'"
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
                self._logger.info(f"{self._prefix_msg()} '{input_name}' loaded!")
            return config, failure

    def _load_file(self, file_path: str):
        input_name = os.path.split(file_path)[1]
        extension = os.path.splitext(input_name)[1].strip(".")
        with open(file_path, "rb") as file:
            if extension.lower() == "toml":
                return tomlkit.load(file)
            elif extension.lower() == "ini":
                return IniFileParser.load(file)
            elif extension.lower() == "json":
                return json.load(file)
            else:
                not_implemented_msg = f"{self._prefix_msg()} File extension '{extension}' is not supported"
                raise NotImplementedError(not_implemented_msg)

    def _validate_load(self, raw_config: dict) -> dict:
        """
        Performs default config validation.

        Parameters
        ----------
        raw_config : dict
            The raw, unvalidated config.

        Returns
        -------
        dict
            The validated config.
        """
        if self.validation_model:
            self.validation_model.model_validate(raw_config)
            config = self.validation_model.model_dump()
            self._check_missing_fields(raw_config, config)
            return config
        else:
            self._logger.warning(
                f"{self._prefix_msg()} Cannot validate config. Validation model is {type(self.validation_model).__name__}"
            )
        return raw_config

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
        success, no_old_value = True, False
        try:
            try:
                old_value = self.get_value(key, path)
            except KeyError as e:
                if not create_missing:
                    raise e
                no_old_value = True
            super().set_value(key, value, path, create_missing)
            if self.validation_model:
                self.validation_model.model_validate(self._dict)
        except ValidationError as err:
            success = False
            self._logger.warning(
                f"{self._prefix_msg()} Unable to validate value '{value}' for key '{key}': "
                + format_validation_error(err)
            )
            if no_old_value:
                self.remove_value(key, path)
            else:
                super().set_value(key, old_value, path, False)
        except Exception:
            success = False
            self._logger.error(
                f"{self._prefix_msg()} An unexpected error occurred while validating value '{value}' using key '{key}'\n"
                + traceback.format_exc(limit=CoreArgs._core_traceback_limit),
                gui=True,
            )
        finally:
            if success:
                core_signalbus.configUpdated.emit(
                    (self.name, self.template.name), key, (value,), path
                )
                self._is_modified = True
            return success

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
