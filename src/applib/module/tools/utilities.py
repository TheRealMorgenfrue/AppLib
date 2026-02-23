from collections.abc import Iterable
from typing import Any


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
            None if `search_param` wasn't found in the input.

    """
    if isinstance(input, dict):
        value = input.get(search_param, None)  # search_param is a key mapping to value
        if not value:
            for k, v in input.items():  # search_param is a value mapping to key
                if v == search_param:
                    return k
        return value
