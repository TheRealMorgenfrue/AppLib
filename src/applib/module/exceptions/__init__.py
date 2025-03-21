class MissingFieldError(ValueError):
    pass


class InvalidMasterKeyError(KeyError):
    pass


class IniParseError(ValueError):
    pass


class OrphanGroupWarning(RuntimeWarning):
    pass


class TreeLookupError(LookupError):
    pass
