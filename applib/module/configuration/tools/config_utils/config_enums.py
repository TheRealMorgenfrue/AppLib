from enum import Enum


class ConfigLoadOptions(Enum):
    WRITE_CONFIG = 0
    """Change files on the file system to recover from soft errors. For example creating a backup file."""

    MERGE_INPUT_DATA = 1
    """The data to load is meant to be merged into the config. As such, missing field validation is disabled."""
