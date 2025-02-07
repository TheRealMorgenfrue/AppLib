from typing import Any, Iterable, Optional

from pydantic import ValidationError


def iter_to_str(arg: Iterable, separator: str = "") -> str:
    """
    Converts an iterable into a string, optionally separated by a string.

    Parameters
    ----------
    arg : Iterable
        An iterable which may contain arbitrary objects.

    separator : str, optional
        Separate each element in iterable with this string.

    Returns
    -------
    str
        The iterable converted to a string.
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


def dict_lookup(input: dict, search_param: Any) -> Any:
    """
    Searches provided dictionary for first occurence of search_param.
    This search include both keys and values, starting with values.

    Note: This search is NOT recursive!

    Explanation
    ----------
        search_param:
            Key or value to search for.

        returns:
            Key if `search_param` == value (or vice versa).
            `None` if `search_param` wasn't found in the input.

    """
    if isinstance(input, dict):
        value = input.get(search_param, None)  # search_param is a key mapping to value
        if not value:
            for k, v in input.items():  # search_param is a value mapping to key
                if v == search_param:
                    return k
        return value


def format_validation_error(
    err: ValidationError, include_url: bool = False, include_input: bool = True
) -> str:
    """
    Format a validation error.

    Parameters
    ----------
    err : ValidationError
        An instance of a ValidationError which should be formatted.

    include_url : bool, optional
        Include a url to the Pydantic help page for this error.
        By default `False`.

    include_input : bool, optional
        Include the user input which caused this error.
        By default `True`.

    Returns
    -------
    str
        A formatted string of the ValidationError instance.
    """
    if not isinstance(err, ValidationError):
        raise TypeError(
            f"must be an instance of {ValidationError.__name__}. Got '{type(err).__name__}'"
        )

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

        msg += f"  {error.get("msg")} [{iter_to_str(details, separator=", ")}]\n"
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


def check_dict_nestingLevel(input: dict, stop_at: int) -> bool:
    stack = [iter(input.items())]
    nestingLevel = 0
    while stack:
        for k, v in stack[-1]:
            if isinstance(v, dict):
                stack.append(iter(v.items()))
                nestingLevel += 1
                break
        else:
            if nestingLevel == stop_at:
                return True
            elif nestingLevel > stop_at:
                return False
            stack.pop()
    return False


def format_list_for_display(
    input: list[str], display_items: int = 15, join_string: str = "\n"
) -> str:
    """
    Format arbitrary length lists for screen (or log) display.

    Parameters
    ----------
    input : list[str]
        List to format.

    display_items : int, optional
        How many list items to display before truncating, by default `15`.

    join_string : str, optional
        String used to join() strings in the list, by default `\\n`.

    Returns
    -------
    list[str]
        The formatted list.
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


def retrieve_dict_value(
    d: dict,
    key: str,
    parent_key: Optional[str] = None,
    default: Any = None,
    get_parent_key: bool = False,
) -> Any | tuple[Any, str]:
    """
    Return first value found.
    If key does not exists, return default.

    Has support for defining search scope with the parent key.
    A value will only be returned if it is within parent key's scope.

    Parameters
    ----------
    d : dict
        The dictionary to search for `key`.

    key : str
        The key to search for.

    parent_key : str, optional
        Limit the search scope to the children of this key.

    default : Any, optional
        The value to return if `key` was not found.
        Defaults to `None`.

    get_parent_key : bool, optional
        Return the immediate parent of `key`.
        Defaults to `False`.

    Returns
    -------
    Any
        The value mapped to `key`, if it exists. Otherwise, `default`.

    tuple[Any, str]
        [0]: The value mapped to the key, if it exists. Otherwise, default.
        [1]: The immediate parent of the supplied key, if `get_parent_key` is `True`. Otherwise, `None`.
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


def insert_dict_value(
    input: dict, key: str, value: Any, parent_key: Optional[str] = None
) -> Any:
    """
    Recursively look for key in input.
    If found, replace the original value with the provided value and return the original value.

    Has support for defining search scope with the parent key.
    Value will only be returned if it is within parent key's scope.

    Note: If a nested dict with multiple identical parent_keys exist,
    only the top-most parent_key is considered.

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
        By default `None`.

    Returns
    -------
    Any
        The replaced old value.

    Raises
    ------
    KeyError
        If `key` was not found in the config.
    """
    old_value = []  # Modified in-place by traverseDict
    parent_keys = []

    def traverseDict(
        _input: dict, search_key: str, value: Any, _parent_key: str
    ) -> None:
        """
        Recursively search through `_input` depth-first.

        Parameters
        ----------
        _input : dict
            Dict to search in.

        search_key : str
            The key to search for.

        value : Any
            The value assigned to `search_key`.

        _parent_key : str
            `search_key` must have this key as a parent.
        """
        for traverse_key, traverse_value in _input.items():
            # We've found the value we're looking for
            if old_value:
                break

            # The dict is still nested
            if isinstance(traverse_value, dict):
                parent_keys.append(traverse_key)
                traverseDict(traverse_value, search_key, value, _parent_key)

            # The key is what we're looking for
            if traverse_key == search_key:
                # The key need a parent to be considered relevant
                if parent_key:
                    # The key has the correct parent key
                    if _parent_key in parent_keys:
                        _input[traverse_key] = value
                        old_value.append(traverse_value)
                # The key does not need a parent
                else:
                    _input[traverse_key] = value
                    old_value.append(traverse_value)
                break

    traverseDict(input, key, value, parent_key)
    if not old_value:
        raise KeyError(f"Key '{key}' does not exists")
    return old_value[0]
