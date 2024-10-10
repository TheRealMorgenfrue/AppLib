import os
import shutil
import tomlkit
import tomlkit.exceptions
import json
import traceback

from pathlib import Path
from pydantic import ValidationError
from typing import Any, Callable, Mapping, Optional

from module.config.internal.app_args import AppArgs
from module.config.tools.ini_file_parser import IniFileParser
from module.exceptions import IniParseError, InvalidMasterKeyError, MissingFieldError
from module.logging import logger
from module.tools.types.general import Model, NestedDict, StrPath
from module.tools.utilities import formatValidationError


def writeConfig(
    config: dict | Model,
    dst_path: StrPath,
    comments: Optional[Any] = None,
    sort: bool = False,
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

    comments : Any, optional
        Comments associated with the settings in the config which will
        be written to the config file alongside the config.
        Note: Does not currently work.
        By default None.

    sort : bool, optional
        Sort the Python config object by section name before writing.
        By default False.
    """
    dst_dir = Path(os.path.dirname(dst_path))
    file = os.path.split(dst_path)[1]
    extension = os.path.splitext(dst_path)[1].strip(".")
    try:
        dst_dir.mkdir(parents=True, exist_ok=True)

        if isinstance(config, Model):
            config = config.model_dump()
        if sort and isinstance(config, dict):
            config = dict(
                sorted(config.items())
            )  # Sort the dictionary by section, i.e. top-level keys

        if extension.lower() == "toml":
            _generateTOMLconfig(config, dst_path, comments)
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


def _generateTOMLconfig(config: dict, dstPath: StrPath, comments: Any) -> None:
    """Convert a Python config object to the '.toml'-format and write it to a '.toml' file.

    Parameters
    ----------
    config : dict
        A Python config object.

    dstPath : StrPath
        Path-like object pointing to a toml file.
        Note: the file does not have to exist.

    comments : Any
        Comments associated with the settings in the config.
    """
    fileName = os.path.split(dstPath)[1]
    doc = tomlkit.document()
    prevWasComment = False
    for section, keys in config.items():
        table = tomlkit.table()
        for i, key in enumerate(keys):
            if comments:
                if hasattr(comments, key):
                    prevWasComment = True
                    if i != 0:  # Do not make newline right after section
                        table.add(tomlkit.nl())
                    for comment in comments.__getattribute__(
                        key
                    ):  # Write multi-line comments
                        table.add(tomlkit.comment(comment))
                elif prevWasComment:
                    table.add(tomlkit.nl())
            prevWasComment = False
            table.append(key, keys[key])
        doc.append(section, table)

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
    iniConfig = ""
    fileName = os.path.split(dstPath)[1]
    for section in config:
        keys = config[section]
        table = ""
        for key in keys:
            table += f"{key} = {keys[key]}\n"
        table += "\n"
        iniConfig += f"[{section}]" + "\n" + table

    with open(dstPath, "w", encoding="utf-8") as file:
        logger.debug(f"Writing '{fileName}' to '{dstPath}'")
        file.write(iniConfig)


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


def checkMissingFields(raw_config: dict, template_config: dict) -> None:
    """Compare the raw_config against the template_config for missing
    sections/settings and vice versa.

    Parameters
    ----------
    raw_config : dict
        A config read from a file.

    template_config : dict
        The template version of the raw config file.

    Raises
    ------
    MissingFieldError
        If any missing or unknown sections/settings are found.
    """
    allErrors, sectionErrors, fieldErrors = [], [], []
    for section in template_config:  # Check sections
        sectionExistsInConfig = section in raw_config
        if not sectionExistsInConfig:
            sectionErrors.append(f"Missing section '{section}'")
        else:
            for setting in template_config[section]:  # Check settings in a section
                if sectionExistsInConfig and setting not in raw_config[section]:
                    fieldErrors.append(
                        f"Missing setting '{setting}' in section '{section}'"
                    )

    for section in raw_config:  # Check sections
        sectionShouldExist = section in template_config
        if not sectionShouldExist:
            if isinstance(raw_config[section], dict):
                sectionErrors.append(f"Unknown section '{section}'")
            else:
                # NOTE: Sectionless settings are interpreted as sections by the parser
                fieldErrors.append(f"Setting '{section}' does not belong to a section")
        else:
            for setting in raw_config[section]:  # Check settings in a section
                if sectionShouldExist and setting not in template_config[section]:
                    fieldErrors.append(
                        f"Unknown setting '{setting}' in section '{section}'"
                    )
    # Ensure all section errors are displayed first
    allErrors.extend(sectionErrors)
    allErrors.extend(fieldErrors)
    if len(allErrors) > 0:
        raise MissingFieldError(allErrors)


def retrieveDictValue(
    d: dict,
    key: str,
    parent_key: Optional[str] = None,
    default: Any = None,
    get_parent_key: bool = False,
) -> Any | tuple[Any, str]:
    """Return first value found.
    If key does not exists, return default.

    Has support for defining search scope with the parent key.
    A value will only be returned if it is within parent key's scope

    Parameters
    ----------
    d : dict
        The dictionary to search for key.

    key : str
        The key to search for.

    parent_key : str, optional
        Limit the search scope to the children of this key.

    default : Any, optional
        The value to return if the key was not found.
        Defaults to None.

    get_parent_key : bool, optional
        Return the immediate parent of the supplied key.
        Defaults to False.

    Returns
    -------
    Any
        The value mapped to the key, if it exists. Otherwise, default.

    tuple[Any, str]
        If `get_parent_key` is True
        [0]: The value mapped to the key, if it exists. Otherwise, default.
        [1]: The immediate parent of the supplied key, if any. Otherwise, None.
    """
    stack = [iter(d.items())]
    parent_keys = []
    found_value = default
    immediate_parent = None
    while stack:
        for k, v in stack[-1]:
            if k == key:
                if get_parent_key:
                    immediate_parent = parent_keys[-1]
                if parent_key:
                    if parent_key in parent_keys:
                        found_value = v
                        stack.clear()
                        break
                else:
                    found_value = v
                    stack.clear()
                    break
            elif isinstance(v, dict):
                stack.append(iter(v.items()))
                parent_keys.append(k)
                break
        else:
            stack.pop()
            if parent_keys:
                parent_keys.pop()
    return (found_value, immediate_parent) if get_parent_key else found_value


def insertDictValue(
    input: dict, key: str, value: Any, parent_key: Optional[str] = None
) -> list | None:
    """
    Recursively look for key in input.
    If found, replace the original value with the provided value and return the original value.

    Has support for defining search scope with the parent key.
    Value will only be returned if it is within parent key's scope.

    Note: If a nested dict with multiple identical parent_keys exist,
    only the top-most parent_key is considered

    Causes side-effects!
    ----------
    Modifies input in-place (i.e. does not return input).

    Parameters
    ----------
    input : dict
        The dictionary to search in.

    key : str
        The key to look for.

    value : Any
        The value to insert.

    parent_key : str, optional
        Limit the search scope to the children of this key.
        By default None.

    Returns
    -------
    list | None
        The replaced old value, if found. Otherwise, None.
    """
    old_value = []  # Modified in-place by traverseDict
    parentKeys = []

    def traverseDict(_input: dict, _key, _value, _parent_key) -> list | None:
        for k, v in _input.items():
            if old_value:
                break
            if isinstance(v, dict):
                parentKeys.append(k)
                traverseDict(v, _key, _value, _parent_key)
            elif k == _key:
                if parent_key:
                    if _parent_key in parentKeys:
                        _input[k] = _value
                        old_value.append(v)
                else:
                    _input[k] = _value
                    old_value.clear()
                    old_value.append(v)
                break

    traverseDict(input, key, value, parent_key)
    return old_value or None


def loadConfig(
    config_name: str,
    config_path: StrPath,
    validator: Optional[Callable[[Mapping], dict[str, Any]]] = None,
    template_config: Optional[dict[str, Any]] = None,
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

    template_config : dict[str, Any] | None, optional
        A validated config created by the supplied validation model.
        NOTE: Must be supplied if *do_write_config* is True.
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
        Note: This has no effect if *doWriteConfig* is False.
        By default 1.

    Returns
    -------
    tuple[dict[str, Any] | None, bool]
        Returns a tuple of values:
        * [0]: The config file converted to a Python object (dict)
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
            writeConfig(template_config, config_path)
    except MissingFieldError as err:
        isError, isRecoverable = True, True
        err_msg = f"{config_name}: Detected incorrect fields in '{filename}':\n"
        for item in err.args[0]:
            err_msg += f"  {item}\n"
        logger.warning(err_msg)
        if do_write_config:
            logger.info(f"{config_name}: Repairing config")
            repairedConfig = upgradeConfig(raw_config, template_config)
            backupConfig(config_path)
            writeConfig(repairedConfig, config_path)
    except (InvalidMasterKeyError, AssertionError) as err:
        isError, isRecoverable = True, True
        logger.warning(f"{config_name}: {err.args[0]}")
        if do_write_config:
            backupConfig(config_path)
            writeConfig(template_config, config_path)
    except (tomlkit.exceptions.ParseError, IniParseError) as err:
        isError, isRecoverable = True, True
        logger.warning(
            f"{config_name}: Failed to parse '{filename}':\n  {err.args[0]}\n"
        )
        if do_write_config:
            backupConfig(config_path)
            writeConfig(template_config, config_path)
    except FileNotFoundError:
        isError, isRecoverable = True, True
        logger.info(f"{config_name}: Creating '{filename}'")
        if do_write_config:
            writeConfig(template_config, config_path)
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
                    template_config=template_config,
                    do_write_config=do_write_config,
                    retries=retries - 1,
                )
                if not use_validator_on_error:
                    failure = True
            else:
                failure = True
                load_failure_msg = f"{config_name}: Failed to load '{filename}'"
                if template_config:
                    load_failure_msg += ". Switching to template config"
                    config = template_config  # Use template config if all else fails
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
    """Validate a value in the supplied config.

    Parameters
    ----------
    config_name : str
        The name of the *config*.

    config : dict
        A Python config object.

    validator : Callable[[dict], dict]
        The validator callable which validates the config.

    key : str
        The key whose value should be updated.

    value : Any
        The value whose should be saved.

    parent_key : str | None, optional
        *key* must exists with the scope of this key.

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
        insertDictValue(config, setting, old_value[0])  # Restore value
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


# TODO: Each config should specify a method for upgrading it
def upgradeConfig(
    validated_config: NestedDict, template_config: NestedDict
) -> NestedDict:
    """Preserve all valid values in the config when some fields are determined invalid.
    Note: does not support sectionless configs.

    Parameters
    ----------
    validated_config : NestedDict
        The config, loaded from disk and validated, which contains invalid fields.

    template_config : NestedDict
        The template of the *validated_config*.

    Returns
    -------
    NestedDict
        The config where all values are valid with as many as possible
        preserved from the *validated_config*.
    """
    # TODO: Add support for sectionless configs
    new_config = {}
    for section_name, section in template_config.items():
        new_config |= {section_name: {}}
        for setting, options in section.items():
            if (
                section_name in validated_config
                and setting in validated_config[section_name]
            ):
                new_config[section_name] |= {
                    setting: validated_config[section_name][setting]
                }
            else:
                new_config[section_name] |= {setting: options}
    return new_config
