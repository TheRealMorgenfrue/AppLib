import os
from typing import SupportsIndex, SupportsInt, TypeAlias, Union

from pydantic import BaseModel
from PyQt6.QtGui import QIcon
from qfluentwidgets import FluentIconBase
from typing_extensions import Buffer

ReadableBuffer: TypeAlias = Buffer
ConvertibleToInt: TypeAlias = str | ReadableBuffer | SupportsInt | SupportsIndex
StrPath: TypeAlias = str | os.PathLike[str]
floatOrInt: TypeAlias = float | int

Model: TypeAlias = BaseModel
"""A Pydantic validation model (not constructed)"""

iconDict: TypeAlias = dict[str, str | QIcon | FluentIconBase]
"""Maps a template section name to an icon"""
