from typing import override

from PyQt6.QtGui import QColor

from .converter import Converter


class ColorConverter(Converter):
    def __init__(self):
        super().__init__()

    @override
    def convert(self, value: QColor | str, to_gui=False):
        value = QColor(value)
        return value if to_gui else value.name()
