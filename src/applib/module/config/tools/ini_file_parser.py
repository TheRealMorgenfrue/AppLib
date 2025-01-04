import re
from typing import IO, Union

from ...exceptions import IniParseError
from ...tools.utilities import decodeInput


class IniFileParser:
    @classmethod
    def _getBool(cls, value):
        value = str(value).lower()
        if value in ("y", "yes", "t", "true"):
            return True
        elif value in ("n", "no", "f", "false"):
            return False
        else:
            raise ValueError(f"invalid truth value '{value}'")

    @classmethod
    def _getNumber(cls, value: str) -> Union[float, int, str]:
        """Returns value if not number"""
        try:
            if value.count(".") == 1:
                value = float(value)
            else:
                value = int(value)
        except ValueError:
            pass
        return value

    @classmethod
    def load(cls, fp: IO[str] | IO[bytes]) -> dict:
        """Read a .ini file and convert it to a Python object.

        Parameters
        ----------
        fp : IO[str] | IO[bytes]
            An IO file pointer.

        Returns
        -------
        dict
            The content of the file converted to a Python object.
        """
        file_content = decodeInput(fp.read()).splitlines()
        config = {}
        kv_list, sections, keys, values = [], [], [], []
        current_section = None
        # Contains 2 capture groups: Section, Key/Value
        pattern = re.compile(r"(?<!.)\[(.*)\]|((?<!.).+)")
        for i, line in enumerate(file_content):
            if line == "":
                continue
            match = re.search(pattern, line)

            found_section = match.group(1)
            if found_section is None:
                try:
                    key, value = match.group(2).split("=", maxsplit=1)
                except ValueError:
                    err_msg = f"Unexpected input '{line}' at line {i+1}"
                    raise IniParseError(err_msg) from None

                if not key:
                    err_msg = f"Illegal key '{key}' at line {i+1}"
                    raise IniParseError(err_msg)

                # Add key/value pair to list of parsed pairs
                keys.append(key.strip())
                value = value.strip()
                try:
                    converted_value = cls._getBool(value)
                except ValueError:
                    converted_value = cls._getNumber(value)
                values.append(converted_value)
            else:
                # Save the current section's key/value pairs
                if current_section is not None:
                    kv_list.append(dict(zip(keys, values)))
                    keys.clear()
                    values.clear()
                # Sectionless key/value pairs
                else:
                    config |= dict(zip(keys, values))
                    keys.clear()
                    values.clear()
                # Prepare the new section
                current_section = found_section
                sections.append(current_section)
        else:
            # Save the final section's key/value pairs
            if current_section is not None:
                kv_list.append(dict(zip(keys, values)))
            # Sectionless ini file
            else:
                config |= dict(zip(keys, values))

        config |= dict(zip(sections, kv_list))
        return config
