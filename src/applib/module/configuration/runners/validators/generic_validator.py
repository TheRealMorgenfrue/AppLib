import re
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


def validate_proxy_address(proxyAddress: str) -> str:
    """Validates a proxy address using a regex pattern

    Parameters
    ----------
    proxyAddress : str

    Returns
    -------
    str
        The proxy address, if valid

    Raises
    ------
    AssertionError
        The proxy address is invalid
    """
    if proxyAddress != "":
        match = re.match(
            r"^(?:(https?|socks[45]h?)://)?([\w.-]+)(:\d+)?$", proxyAddress
        )
        if not match:
            err_msg = f"Invalid proxy address: '{proxyAddress}'"
            raise AssertionError(err_msg)
    return proxyAddress
