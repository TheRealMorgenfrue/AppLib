from typing import TypeAlias

from PyQt6.QtGui import QIcon
from qfluentwidgets import FluentIconBase


iconDict: TypeAlias = dict[str, str | QIcon | FluentIconBase]
"""Maps a template section name to an icon"""
