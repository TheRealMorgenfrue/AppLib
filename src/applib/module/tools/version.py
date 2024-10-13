"""The `version` module holds the version information for the app."""

from __future__ import annotations as _annotations

__all__ = "VERSION"

VERSION = "0.0.1"
"""The version of the app."""


def version_short() -> str:
    """Return the `major.minor` part of the app's version.

    It returns '2.1' if app version is '2.1.1'.
    """
    return ".".join(VERSION.split(".")[:2])