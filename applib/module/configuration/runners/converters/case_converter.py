from enum import Enum
from typing import Any, override

from .converter import Converter


class Case(Enum):
    UPPER = str.upper
    LOWER = str.lower
    CAPITALIZE = str.capitalize
    TITLE = str.title


class CaseConverter(Converter):
    def __init__(self, config_case: Case | Any, gui_case: Case | Any):
        """
        Create a case converter for a setting.
        This converter is suitable for changing cases of strings.

        Parameters
        ----------
        config_case : Case
            The case present in the config.

        gui_case : Case
            The case to be displayed in the GUI.
        """
        super().__init__()
        self.config_case = config_case
        self.gui_case = gui_case

    @override
    def convert(self, value: str, to_gui: bool = False) -> str:
        if to_gui:
            return self.gui_case.value(value)
        else:
            return self.config_case.value(value)
