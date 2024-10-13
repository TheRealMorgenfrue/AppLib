from pathlib import Path
from qfluentwidgets import StyleSheetBase, Theme, qconfig

from enum import Enum


class CoreStyleSheet(StyleSheetBase, Enum):
    # Interfaces
    MAIN_WINDOW = "main_window"
    HOME_INTERFACE = "home_interface"
    PROCESS_INTERFACE = "process_interface"
    SETTINGS_INTERFACE = "settings_interface"
    SETTINGS_SUBINTERFACE = "settings_subinterface"

    # Components
    CONSOLE_VIEW = f"components/console_view"
    INPUT_VIEW = f"components/input_view"
    LINK_CARD = f"components/link_card"
    PROGRESS_BAR = f"components/progress_bar"
    SAMPLE_CARD = f"components/sample_card"
    SETTING_WIDGET = f"components/setting_widget"
    SETTING_CARD = f"components/setting_card"

    def path(self, theme=Theme.AUTO):
        theme = qconfig.theme if theme == Theme.AUTO else theme
        return (
            f"{Path(f"assets/qss/{theme.value.lower()}/{self.value}.qss").absolute()}"
        )
