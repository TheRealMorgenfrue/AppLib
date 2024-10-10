from typing import Any
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
