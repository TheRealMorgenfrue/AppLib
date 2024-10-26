from typing import Any, Optional
from pydantic import ValidationError
from typing import Iterable


def iterToString(arg: Iterable, separator: str = "") -> str:
    """Converts an iterable into a string, optionally separated by a string

    Parameters
    ----------
    arg : Iterable
        An iterable which may contain arbitrary objects

    separator : str, optional
        Separate each element in iterable with this string

    Returns
    -------
    str
        The iterable converted to a string
    """
    if arg is None:
        return f"{arg}"

    string = ""
    for i, item in enumerate(arg):
        if i == len(arg) - 1:
            string += f"{item}"
        else:
            string += f"{item}" + separator
    return string


def dictLookup(input: dict, search_param: Any) -> Any:
    """Searches provided dictionary for first occurence of search_param.\n
    This search include both keys and values, starting with values.

    Note: This search is NOT recursive!

    Explanation
    ----------
        search_param:
            Key or Value to search for

        returns:
            Key if search_param == Value (or vice versa)\n
            None if search_param wasn't found in the input

    """
    if isinstance(input, dict):
        value = input.get(search_param, None)  # searchParam is a key mapping to value
        if not value:
            for k, v in input.items():  # searchParam is a value mapping to key
                if v == search_param:
                    return k
        return value


def formatValidationError(
    err: ValidationError, include_url: bool = False, include_input: bool = True
) -> str:
    """Format a validation error

    Parameters
    ----------
    err : ValidationError
        An instance of a ValidationError which should be formatted.

    include_url : bool, optional
        Include a url to the Pydantic help page for this error.
        Defaults to False.

    include_input : bool, optional
        Include the user input which caused this error.
        Defaults to True.

    Returns
    -------
    str
        A formatted string of the ValidationError instance.
    """
    assert isinstance(
        err, ValidationError
    ), f"Must be an instance of {ValidationError.__name__}"
    errors = err.errors(include_url=include_url, include_input=include_input)

    error_count = err.error_count()
    msg = f"{error_count} validation error{"s" if error_count > 1 else ""} for '{err.title}'\n"
    for error in errors:
        section = error.get("loc")[0]
        setting = error.get("loc")[1]
        msg += f"{section}.{setting}\n"

        error_type = f"type={error.get("type")}"
        input_value = f"input_value={error.get("input")}" if include_input else ""
        input_type = f"input_type={type(error.get("input")).__name__}"
        details = [error_type, input_value, input_type]

        msg += f"  {error.get("msg")} [{iterToString(details, separator=", ")}]\n"
        msg += (
            f"    For further information visit {error.get("url")}\n"
            if include_url
            else ""
        )
    return msg


def decodeInput(input: str | bytes, encoding: str = "utf-8") -> str:
    if isinstance(input, str):
        return input
    return input.decode(encoding=encoding, errors="ignore")


def getDictNestingLevel(input: dict, stop_at: int) -> int:
    stack = [iter(input.items())]
    nestingLevel = 0
    while stack:
        if nestingLevel == stop_at:
            return nestingLevel
        for k, v in stack[-1]:
            if isinstance(v, dict):
                stack.append(iter(v.items()))
                nestingLevel += 1
                break
            else:
                return nestingLevel
        else:
            stack.pop()


def formatListForDisplay(
    input: list[str], display_items: int = 15, join_string: str = "\n"
) -> str:
    """Format arbitrary length lists for screen (or log) display.

    Parameters
    ----------
    input : list[str]
        List to format

    display_items : int, optional
        How many list items to display before truncating, by default 15

    join_string : str, optional
        String used to join() strings in the list, by default "\\n"

    Returns
    -------
    list[str]
        The formatted list
    """
    input_size = len(input)
    do_truncate = display_items != -1 and input_size > display_items + 1
    silent = display_items == 0
    if silent:
        join_string = ""

    truncated_msg = (
        ""
        if silent
        else (
            f"\n{join_string}(not showing {input_size-display_items} entries)"
            if do_truncate
            else ""
        )
    )
    return f"{join_string.join(input[0:display_items] if do_truncate else input)}{truncated_msg}"


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
                if parent_key is not None:
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
