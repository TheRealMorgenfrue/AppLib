from enum import Enum
from typing import Final

SEARCH_SEP: Final = "/"
"""The path separator used in search"""


class SearchMode(Enum):
    STRICT = 0
    """The search path must be absolute. Always returns the correct result."""
    FUZZY = 2
    """The search path may be relative. May return an incorrect result in certain situations.\n
    E.g. duplicate keys with an empty search_path parameter."""
