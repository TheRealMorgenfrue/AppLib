from typing import override

from .generic_converter import GenericConverter


class CMDConverter(GenericConverter):
    def __init__(self, config_values, gui_values):
        super().__init__(config_values, gui_values)

    @override
    def convert(self, value, to_gui=False):
        # Intentionally a no-op
        return value

    def getArgument(self, value):
        return super().convert(value)
