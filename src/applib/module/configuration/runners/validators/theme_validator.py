from ...internal.core_args import CoreArgs


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
