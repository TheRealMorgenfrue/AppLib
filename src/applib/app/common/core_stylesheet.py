from enum import Enum

from qfluentwidgets import StyleSheetBase, Theme, qconfig

from ...module.configuration.internal.core_args import CoreArgs


class CoreStyleSheet(StyleSheetBase, Enum):
    # Interfaces
    MAIN_WINDOW = "main_window"
    HOME_INTERFACE = "home_interface"
    PROCESS_INTERFACE = "process_interface"
    SETTINGS_INTERFACE = "settings_interface"
    SETTINGS_SUBINTERFACE = "settings_subinterface"
    GENERIC = "generic"

    # Components
    CONSOLE_VIEW = "components/console_view"
    INPUT_VIEW = "components/input_view"
    LINK_CARD = "components/link_card"
    PROGRESS_BAR = "components/progress_bar"
    SAMPLE_CARD = "components/sample_card"
    SETTING_WIDGET = "components/setting_widget"
    SETTING_CARD = "components/setting_card"

    def path(self, theme=Theme.AUTO):
        theme = qconfig.theme if theme == Theme.AUTO else theme
        return f"{CoreArgs._core_qss_dir}/{theme.value.lower()}/{self.value}.qss"
