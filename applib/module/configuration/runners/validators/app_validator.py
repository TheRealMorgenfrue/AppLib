import os

from ....logging.logging_manager import LoggingManager
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
    ValueError
        The loglevel is invalid.
    """
    loglevel = loglevel.upper()
    if loglevel not in LoggingManager.LogLevel._member_names_:
        err_msg = (
            f"Invalid log level '{loglevel}'. "
            + f"Expected one of '{LoggingManager.LogLevel._member_names_}'"
        )
        raise ValueError(err_msg)
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
    ValueError
        The theme is invalid.
    """
    if theme not in CoreArgs._core_template_themes:
        err_msg = f"Invalid theme '{theme}'. Expected one of '{CoreArgs._core_template_themes}'"
        raise ValueError(err_msg)
    return theme


def validate_background(image_path: str) -> str:
    if image_path and not os.path.isfile(image_path):
        err_msg = f"Invalid background '{image_path}'. A background must be a file."
        raise ValueError(err_msg)
    return image_path
