import re
from pathlib import Path


def validate_path(path: str) -> str:
    """Ensure a path exists.

    Parameters
    ----------
    path : str

    Returns
    -------
    path
        The path, if it exists.

    Raises
    ------
    ValueError
        The path does not exist.
    """
    if not Path(path).exists() and not Path(path).resolve().exists():
        err_msg = f"'{path}' does not exist on the filesystem"
        raise ValueError(err_msg)
    return path


def validate_proxy_address(proxy_address: str) -> str:
    """Validate a proxy address using a RegEx pattern.

    Parameters
    ----------
    proxy_address : str

    Returns
    -------
    str
        The proxy address, if valid.

    Raises
    ------
    ValueError
        The proxy address is invalid.
    """
    if proxy_address != "":
        if not re.match(
            r"^(?:(https?|socks[45]h?)://)?([\w.-]+)(:\d+)?$", proxy_address
        ):
            err_msg = f"Invalid proxy address: '{proxy_address}'"
            raise ValueError(err_msg)
    return proxy_address


def validate_ip_address(ip_address: str) -> str:
    """Validate an IPv4 or IPv6 address using RegEx patterns.

    Parameters
    ----------
    ip_address : str

    Returns
    -------
    str
        The IP address, if valid.

    Raises
    ------
    ValueError
        The IP address is invalid.
    """
    if ip_address != "":
        # ipv4
        if re.match(
            r"^((?:[01]?[0-9]{1,2}|2[0-4][0-9]|25[0-5])\.(?:[01]?[0-9]{1,2}|2[0-4][0-9]|25[0-5])\.(?:[01]?[0-9]{1,2}|2[0-4][0-9]|25[0-5])\.(?:[01]?[0-9]{1,2}|2[0-4][0-9]|25[0-5]))$",
            ip_address,
        ):
            pass
        # ipv6
        elif re.match(
            r"(?:^|(?<=\s))(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))(?=\s|$)",
            ip_address,
        ):
            pass
        else:
            err_msg = f"Invalid IP address: '{ip_address}'"
            raise ValueError(err_msg)
    return ip_address
