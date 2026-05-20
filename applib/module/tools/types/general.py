import os
from collections.abc import Buffer
from typing import SupportsIndex, SupportsInt

from PyQt6.QtGui import QIcon
from qfluentwidgets import FluentIconBase

type ReadableBuffer = Buffer
type ConvertibleToInt = str | ReadableBuffer | SupportsInt | SupportsIndex
type StrPath = str | os.PathLike[str]
type floatOrInt = float | int


type iconDict = dict[str, str | QIcon | FluentIconBase]
"""Maps a template section name to an icon"""
