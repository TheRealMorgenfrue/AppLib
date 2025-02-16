from typing import Any, override

from ...tools.template_utils.converter import Converter


class GenericConverter(Converter):
    def __init__(self, config_values: list, gui_values: list):
        """
        Create a generic value converter for a setting.
        This converter is suitable for converting between Numbers, Strings, and Booleans.

        Note
        ----
        The list indices are associative, i.e., `config_values[0]` maps to `gui_values[0]`

        Parameters
        ----------
        config_values : list
            Values as they are present in the config.

        gui_values : list
            The config values as they should be displayed in the GUI.
        """
        super().__init__()
        self.config_values = config_values
        self.gui_values = gui_values

    def _convert_value(self, value: Any, source: list, target: list) -> Any:
        try:
            idx = source.index(value)
        except ValueError:
            idx = target.index(value)  # Uncaught value error on purpose
        return target[idx]

    @override
    def convert(self, value: Any, to_gui: bool = False) -> Any:
        if to_gui:
            src, tgt = self.config_values, self.gui_values
        else:
            src, tgt = self.gui_values, self.config_values
        return self._convert_value(value, src, tgt)
