from typing import override

from applib_core import Converter
from PyQt6.QtGui import QColor


class ColorConverter(Converter):
    def __init__(self):
        super().__init__()

    @override
    def convert(self, value: QColor | str, to_gui=False):
        value = QColor(value)
        return value if to_gui else value.name()
