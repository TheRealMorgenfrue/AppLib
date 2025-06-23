from ....logging import LoggingManager
from ...internal.core_args import CoreArgs


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


def validate_theme(theme: str) -> str:
    """Ensure the theme is a valid argument for the app.

    Parameters
    ----------
    theme : str
        The theme, e.g. "Dark".

    Returns
    -------
    str
        The theme, if valid.

    Raises
    ------
    AssertionError
        The theme is invalid.
    """
    if not theme in CoreArgs._core_template_themes:
        err_msg = f"Invalid theme '{theme}'. Expected one of '{CoreArgs._core_template_themes}'"
        raise AssertionError(err_msg)
    return theme
