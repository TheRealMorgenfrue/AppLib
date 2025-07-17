from enum import Enum
from typing import Final

SEARCH_SEP: Final = "/"
"""The path separator used in search"""


class SearchMode(Enum):
    STRICT = 0
    """The search path must be absolute"""
    FUZZY = 2
    """The search path may be relative"""
