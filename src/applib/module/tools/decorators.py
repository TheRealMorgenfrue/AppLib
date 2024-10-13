import sys

from ..config.internal.app_args import AppArgs

# Python module/packaging system explainer: https://stackoverflow.com/a/35710527


def export(func):
    """Function decorator for adding function to __all__ automatically.

    Usage:
    -----
    ```py
    @export
    def foo(): pass
    ```
    """
    mod = sys.modules[func.__module__]
    if hasattr(mod, "__all__"):
        mod.__all__.append(func.__name__)
    else:
        mod.__all__ = [func.__name__]
    return func


def mainArgs(cls):
    for k, v in cls.__dict__.items():
        if k.count("_") != 4:
            setattr(AppArgs, k, v)
    return cls
