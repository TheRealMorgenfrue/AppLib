from enum import Enum


class ConfigLoadOptions(Enum):
    WRITE_CONFIG = 0
    """Change files on the file system to recover from soft errors. For example creating a backup file."""
