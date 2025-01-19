def makeSetupArgs(cls):
    """Class decorator for declaring a class as the main setup arguments for the application."""
    from ..configuration.internal.core_args import CoreArgs

    for k, v in cls.__dict__.items():
        # Ensure in-built attributes are not copied (i.e. prefix or postfix is not "__")
        if k[:2].count("_") != 2 and k[-2:].count("_") != 2:
            setattr(CoreArgs, k, v)
    return cls
