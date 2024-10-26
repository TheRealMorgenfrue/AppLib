from collections import deque
from configparser import ConfigParser
import os
import shutil
import tomlkit
import tomlkit.exceptions
import json
import traceback

from pathlib import Path
from pydantic import ValidationError
from typing import Any, Callable, Literal, Mapping, Optional

from ..internal.app_args import AppArgs
from ..tools.ini_file_parser import IniFileParser
from ...exceptions import IniParseError, InvalidMasterKeyError, MissingFieldError
from ...logging import logger
from ...tools.types.general import Model, StrPath
from ...tools.utilities import formatValidationError, insertDictValue


def writeConfig(
    config: dict | Model,
    dst_path: StrPath,
) -> None:
    """
    Convert and write a Python config object to config files of different types.
    Supports: toml, ini, json.

    Parameters
    ----------
    config : dict | Model
        The Python config object to convert and write to a file.
        Can be an instance of a validation model.

    dst_path : StrPath
        Path-like object pointing to a supported config file.
        Note: the file does not have to exist.
    """
    dst_dir = Path(os.path.dirname(dst_path))
    file = os.path.split(dst_path)[1]
    extension = os.path.splitext(dst_path)[1].strip(".")
    try:
        dst_dir.mkdir(parents=True, exist_ok=True)

        if isinstance(config, Model):
            config = config.model_dump()

        if extension.lower() == "toml":
            _generateTOMLconfig(config, dst_path)
        elif extension.lower() == "ini":
            _generateINIconfig(config, dst_path)
        elif extension.lower() == "json":
            _generateJSONConfig(config, dst_path)
        else:
            logger.warning(f"Cannot write unsupported file '{file}'")
    except Exception:
        logger.error(
            f"Failed to write {file} to '{dst_path}'\n"
            + traceback.format_exc(limit=AppArgs.traceback_limit)
        )
        raise


# TODO: Make recursive
def _generateTOMLconfig(config: dict, dstPath: StrPath) -> None:
    """Convert a Python config object to the '.toml'-format and write it to a '.toml' file.

    Parameters
    ----------
    config : dict
        A Python config object.

    dstPath : StrPath
        Path-like object pointing to a toml file.
        Note: the file does not have to exist.
    """
    fileName = os.path.split(dstPath)[1]
    doc = tomlkit.document()
    for key, value in config.items():
        table = tomlkit.table()
        table.append(key, value)
        doc.append(key, table)

    with open(dstPath, "w", encoding="utf-8") as file:
        logger.debug(f"Writing '{fileName}' to '{dstPath}'")
        tomlkit.dump(doc, file)


def _generateINIconfig(config: dict, dstPath: StrPath) -> None:
    """Convert a Python config object to the '.ini'-format and write it to a '.ini' file.

    Parameters
    ----------
    config : dict
        A Python config object.

    dstPath : StrPath
        Path-like object pointing to a ini file.
        Note: the file does not have to exist.
    """
    document = ""
    q = deque()  # type: deque[dict]
    q.append(config)
    parents = deque()  # type: deque[str]

    while q:
        table = ""
        current_parent = f"{parents[0]}." if parents else ""
        for key, value in q.popleft().items():
            if isinstance(value, dict):
                parents.append(f"{current_parent}{key}")
                q.append(value)
            else:
                table += f"{key} = {value}\n"
        else:
            if table:
                section_header = f"[{parents.popleft()}]" if parents else ""
                document += section_header + "\n"
                document += table + "\n\n"

    fileName = os.path.split(dstPath)[1]
    with open(dstPath, "w", encoding="utf-8") as file:
        logger.debug(f"Writing '{fileName}' to '{dstPath}'")
        file.write("".join(document))


def _generateJSONConfig(config: dict, dstPath: StrPath) -> None:
    """Convert a Python config object to the '.json'-format and write it to a '.json' file.

    Parameters
    ----------
    config : dict
        A Python config object

    dstPath : StrPath
        Path-like object pointing to a JSON file.
        Note: the file does not have to exist.
    """
    fileName = os.path.split(dstPath)[1]
    with open(dstPath, "w", encoding="utf-8") as file:
        logger.debug(f"Writing '{fileName}' to '{dstPath}'")
        file.write(json.dumps(config, indent=4))


def backupConfig(srcPath: StrPath) -> None:
    """Creates a backup of the file at the supplied path, overwriting any existing backup.

    Parameters
    ----------
    srcPath : StrPath
        Path-like object pointing to a file.
    """
    try:
        srcPath = Path(srcPath)
        file = os.path.split(srcPath)[1]
        if srcPath.exists():
            configDst = Path(f"{srcPath}.bak")
            logger.debug(f"Creating backup of '{file}' to '{configDst}'")
            shutil.copyfile(srcPath, configDst)
        else:
            logger.warning(
                f"Cannot create backup of '{file}'. Path '{srcPath}' does not exist"
            )
    except TypeError:  # If input path is None
        logger.error(
            f"Failed to create backup of '{srcPath}'\n"
            + traceback.format_exc(limit=AppArgs.traceback_limit)
        )


def checkMissingFields(config: dict, template: dict) -> None:
    """Compare the config against the template for missing
    sections/settings and vice versa.

    Parameters
    ----------
    config : dict
        The config loaded from a file.

    template : dict
        The template used to create `config`.

    Raises
    ------
    MissingFieldError
        If any missing or unknown sections/settings are found.
    """
    all_errors, section_errors, field_errors = [], [], []
    parents = []

    def searchFields(
        config: dict, template: dict, search_mode: Literal["missing", "unknown"]
    ) -> None:
        """Helper function to keep track of parents while traversing.
        Use `search_mode` to select which type of field to search for.

        Parameters
        ----------
        config : dict
            The config loaded from a file.

        template : dict
            The template used to create `config`.

        search_mode : Literal["missing", "unknown"]
            Specify which type of field to search for.
        """
        # The dict to search depth-first in. Should be opposite of validation dict
        search_dict = template if search_mode == "missing" else config
        # The dict to compare the search dict against. Should be opposite of search dict
        validation_dict = config if search_mode == "missing" else template
        for key, value in search_dict.items():
            # The template is still nested (dict key/value pairs, i.e., sections)
            if isinstance(value, dict):
                if key in validation_dict:  # section exists
                    parents.append(key)
                    next_search = (
                        (config[key], value)
                        if search_mode == "missing"
                        else (value, template[key])
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
                    field_errors.append(f"{search_mode.capitalize()} setting '{key}'")
        else:
            if parents:
                parents.pop()

    searchFields(config, template, search_mode="missing")
    searchFields(config, template, search_mode="unknown")

    # Ensure all section errors are displayed first
    all_errors.extend(section_errors)
    all_errors.extend(field_errors)
    if len(all_errors) > 0:
        raise MissingFieldError(all_errors)


def loadConfig(
    config_name: str,
    config_path: StrPath,
    validator: Optional[Callable[[Mapping], dict[str, Any]]] = None,
    template: Optional[dict[str, Any]] = None,
    do_write_config: bool = True,
    use_validator_on_error: bool = True,
    retries: int = 1,
) -> tuple[dict[str, Any] | None, bool]:
    """Read and validate the config file residing at the supplied config path.

    Parameters
    ----------
    config_name : str
        The name of the config

    config_path : StrPath
        Path-like object pointing to a config file.

    validator : Callable[[Mapping], dict]
        A callable that validates the specific config.
        Must take the raw config as input and return a validated dict instance.

    template : dict[str, Any] | None, optional
        A validated config created by the supplied validation model.
        NOTE: Must be supplied if `do_write_config` is True.
        By default None.

    do_write_config : bool, optional
        Manipulate with files on the file system to recover from soft errors
        (e.g. overwrite the config file with the template config).
        By default True.

    use_validator_on_error : bool, optional
        Use the validator function for the next config reload,
        if the current config failed to load due to a validation error

    retries : int, optional
        Reload the config X times if soft errors occur.
        Note: This has no effect if `do_write_config` is False.
        By default 1.

    Returns
    -------
    tuple[dict[str, Any] | None, bool]
        Returns a tuple of values:
        * [0]: The config file converted to a dict
        * [1]: True if the config failed to load. Otherwise, False

    Raises
    ------
    NotImplementedError
        If the file at the config path is not supported
    """
    isError, failure, reload_failure = False, False, False
    can_reload = do_write_config or not use_validator_on_error
    config = None
    filename = os.path.split(config_path)[1]
    extension = os.path.splitext(filename)[1].strip(".")
    try:
        with open(config_path, "rb") as file:
            if extension.lower() == "toml":
                raw_config = tomlkit.load(file)
            elif extension.lower() == "ini":
                raw_config = IniFileParser.load(file)
            elif extension.lower() == "json":
                raw_config = json.load(file)
            else:
                err_msg = f"{config_name}: Cannot load unsupported file '{config_path}'"
                raise NotImplementedError(err_msg)
        if validator:
            config = validator(raw_config)
        else:
            config = raw_config
    except ValidationError as err:
        isError, isRecoverable = True, True
        logger.warning(f"{config_name}: Could not validate '{filename}'")
        logger.debug(formatValidationError(err))
        if do_write_config:
            backupConfig(config_path)
            writeConfig(template, config_path)
    except MissingFieldError as err:
        isError, isRecoverable = True, True
        err_msg = f"{config_name}: Detected incorrect fields in '{filename}':\n"
        for item in err.args[0]:
            err_msg += f"  {item}\n"
        logger.warning(err_msg)
        if do_write_config:
            logger.info(f"{config_name}: Repairing config")
            repairedConfig = repairConfig(raw_config, template)
            backupConfig(config_path)
            writeConfig(repairedConfig, config_path)
    except (InvalidMasterKeyError, AssertionError) as err:
        isError, isRecoverable = True, True
        logger.warning(f"{config_name}: {err.args[0]}")
        if do_write_config:
            backupConfig(config_path)
            writeConfig(template, config_path)
    except (
        tomlkit.exceptions.ParseError,
        IniParseError,
    ) as err:  # TODO: Add separate except with JSONDecodeError
        isError, isRecoverable = True, True
        logger.warning(
            f"{config_name}: Failed to parse '{filename}':\n  {err.args[0]}\n"
        )
        if do_write_config:
            backupConfig(config_path)
            writeConfig(template, config_path)
    except FileNotFoundError:
        isError, isRecoverable = True, True
        logger.info(f"{config_name}: Creating '{filename}'")
        if do_write_config:
            writeConfig(template, config_path)
    except Exception:
        isError, isRecoverable = True, False
        logger.error(
            f"{config_name}: An unexpected error occurred while loading '{filename}'\n"
            + traceback.format_exc(limit=AppArgs.traceback_limit)
        )
    finally:
        if isError:
            if can_reload and retries > 0 and isRecoverable:
                reload_msg = f"{config_name}: Reloading '{filename}'"
                if not use_validator_on_error:
                    reload_msg += " with compatibility mode"
                logger.info(reload_msg)
                config, reload_failure = loadConfig(
                    config_name=config_name,
                    config_path=config_path,
                    validator=validator if use_validator_on_error else None,
                    template=template,
                    do_write_config=do_write_config,
                    retries=retries - 1,
                )
                if not use_validator_on_error:
                    failure = True
            else:
                failure = True
                load_failure_msg = f"{config_name}: Failed to load '{filename}'"
                if template:
                    load_failure_msg += ". Switching to template config"
                    config = template  # Use template config if all else fails
                    logger.warning(load_failure_msg)
                else:
                    logger.error(load_failure_msg)
        else:
            logger.info(f"{config_name}: Config '{filename}' loaded!")
        return config, failure or reload_failure


def validateValue(
    config_name: str,
    config: dict,
    validator: Callable[[dict], dict],
    setting: str,
    value: Any,
    parent_key: Optional[str] = None,
) -> tuple[bool, bool]:
    """Validate a value in `config`.

    Parameters
    ----------
    config_name : str
        The name of `config`.

    config : dict
        Dict to validate.

    validator : Callable[[dict], dict]
        The validator callable that validates `config`.

    key : str
        The key whose value should be updated.

    value : Any
        The new value to save using `key`.

    parent_key : str | None, optional
        If not None, `key` must exists within the scope of `parent_key`.

    Returns
    -------
    tuple[bool, bool]
        Returns a tuple of values:
        * [0]: True if an error occured.
        * [1]: False if a validation error occurred.
    """
    is_error, is_valid = False, True
    try:
        old_value = insertDictValue(config, setting, value, parent_key=parent_key)
        if old_value is None:
            error_msg = f"Config '{config_name}': Could not find setting '{setting}'"
            raise KeyError(error_msg)
        validator(config, config_name)
    except ValidationError as err:
        is_error, is_valid = True, False
        insertDictValue(
            config, setting, old_value[0], parent_key=parent_key
        )  # Restore value
        logger.warning(
            f"Config '{config_name}': Unable to validate value '{value}' for setting '{setting}': "
            + formatValidationError(err)
        )
    except Exception:
        is_error = True
        logger.error(
            f"Config '{config_name}': An unexpected error occurred while validating value '{value}' using key '{setting}'\n"
            + traceback.format_exc(limit=AppArgs.traceback_limit)
        )
    finally:
        return is_error, is_valid


def repairConfig(config: dict, template: dict) -> dict:
    """Preserve all valid values in `config` when some of its fields are determined invalid.
    Fields are taken from `template` if they could not be preserved from `config`.

    Parameters
    ----------
    config : dict
        The config loaded from a file.

    template : dict
        The template used to create `config`.

    Returns
    -------
    dict
        A new config where all values are valid with as many as possible
        preserved from `config`.
    """
    repaired_config = {}
    for template_key, value in template.items():
        if isinstance(value, dict) and template_key in config:
            # Search config/template recursively, depth-first
            repaired_config |= {template_key: repairConfig(config[template_key], value)}
        elif template_key in config:
            # Preserve value from config
            repaired_config |= {template_key: config[template_key]}
        else:
            # Use value from template
            repaired_config |= {template_key: value}
    return repaired_config
