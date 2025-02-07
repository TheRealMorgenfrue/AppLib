from pathlib import Path


def validate_path(path: str) -> str:
    """Ensure a path exists

    Parameters
    ----------
    path : str

    Returns
    -------
    path
        The path, if it exists

    Raises
    ------
    AssertionError
        The path does not exist
    """
    if not Path(path).exists() and not Path(path).resolve().exists():
        err_msg = f"'{path}' does not exist on the filesystem"
        raise AssertionError(err_msg)
    return path
