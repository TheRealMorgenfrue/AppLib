from ....logging import LoggingManager


def validate_loglevel(loglevel: str) -> str:
    """Ensure `loglevel` follows the loglevel specification.

    Parameters
    ----------
    loglevel : str
        The loglevel, e.g. "DEBUG".

    Returns
    -------
    str
        The loglevel, if valid.

    Raises
    ------
    AssertionError
        The loglevel is invalid.
    """
    loglevel = loglevel.upper()
    if not loglevel in LoggingManager.LogLevel._member_names_:
        err_msg = (
            f"Invalid log level '{loglevel}'. "
            + f"Expected one of '{LoggingManager.LogLevel._member_names_}'"
        )
        raise AssertionError(err_msg)
    return loglevel
