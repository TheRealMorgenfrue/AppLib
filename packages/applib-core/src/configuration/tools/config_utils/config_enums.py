from enum import Enum


class ConfigLoadOptions(Enum):
    WRITE_CONFIG = 0
    """Change files on the file system to recover from soft errors. For example creating a backup file."""

    IGNORE_VALIDATION_ERROR = 1
    """Return the loaded config despite being invalid."""
