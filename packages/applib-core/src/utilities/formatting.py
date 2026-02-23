from pydantic import ValidationError


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
        By default True.

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
    msg = f"{error_count} validation error{'s' if error_count > 1 else ''} for '{err.title}'\n"
    for error in errors:
        section = error.get("loc")[0]
        setting = error.get("loc")[1]
        msg += f"{section}.{setting}\n"

        error_type = f"type={error.get('type')}"
        input_value = f"input_value={error.get('input')}" if include_input else ""
        input_type = f"input_type={type(error.get('input')).__name__}"
        details = [error_type, input_value, input_type]

        msg += f"  {error.get('msg')} [{', '.join(details)}]\n"
        msg += (
            f"    For further information visit {error.get('url')}\n"
            if include_url
            else ""
        )
    return msg


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
            f"\n{join_string}(not showing {input_size - display_items} entries)"
            if do_truncate
            else ""
        )
    )
    return f"{join_string.join(input[0:display_items] if do_truncate else input)}{truncated_msg}"
