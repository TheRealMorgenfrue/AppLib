import os
import tomlkit
import tomlkit.exceptions
import json
import traceback
from collections import deque
from pathlib import Path

from ..internal.core_args import CoreArgs

from ...logging import logger
from ...tools.types.general import Model, StrPath


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
            + traceback.format_exc(limit=CoreArgs.traceback_limit)
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
    for section, keys in config.items():
        table = tomlkit.table()
        for key in keys:
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
