import sys


def export(func):
    """Function decorator for adding function to __all__ automatically.

    Usage:
    -----
    ```py
    @export
    def foo(): pass
    ```
    """
    # Python module/packaging system explainer: https://stackoverflow.com/a/35710527
    mod = sys.modules[func.__module__]
    if hasattr(mod, "__all__"):
        mod.__all__.append(func.__name__)
    else:
        mod.__all__ = [func.__name__]
    return func


def makeAppArgs(cls):
    """Class decorator for declaring a class as the main arguments for the app.

    Must only be used once!
    """
    from ..config.internal.app_args import AppArgs

    for k, v in cls.__dict__.items():
        # Ensure in-built attributes are not copied (i.e. prefix or postfix is not "__")
        if k[:2].count("_") != 2 and k[-2:].count("_") != 2:
            setattr(AppArgs, k, v)
    return cls
