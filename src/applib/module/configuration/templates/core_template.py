from typing import Self, override

from ..internal.core_args import CoreArgs
from ..tools.template_options.actions import change_theme, change_theme_color
from ..tools.template_options.options import (
    ComboBoxOption,
    FileSelectorOption,
    GUIMessage,
    GUIOption,
    NumberOption,
)
from ..tools.template_options.template_enums import UIGroups, UITypes
from ..validators.app_validator import validate_loglevel, validate_theme
from ..validators.generic_validator import validate_path
from .base_template import BaseTemplate


class CoreTemplate(BaseTemplate):
    _instance = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._created = False
        return cls._instance

    def __init__(self) -> None:
        if not self._created:
            super().__init__(
                name=CoreArgs._core_main_template_name,
                template=self._create_template(),
                icons=None,
            )
            self._created = True

    @override
    def _create_template(self) -> dict:
        return {
            "General": {
                "loglevel": ComboBoxOption(
                    default="INFO" if CoreArgs._core_is_release else "DEBUG",
                    actions=[self._logger.setLevel],
                    ui_info=GUIMessage(f"Set log level for {CoreArgs._core_app_name}"),
                    validators=[validate_loglevel],
                    values=CoreArgs._core_template_loglevels,
                )
            },
            "Appearance": {
                "appTheme": ComboBoxOption(
                    default="System",
                    actions=[change_theme],
                    ui_info=GUIMessage("Set application theme"),
                    validators=[validate_theme],
                    values=CoreArgs._core_template_themes,
                ),
                "appColor": GUIOption(
                    default="#2abdc7",
                    actions=[change_theme_color],
                    ui_info=GUIMessage("Set application color"),
                    ui_type=UITypes.COLOR_PICKER,
                ),
                "appBackground": FileSelectorOption(
                    default="",
                    ui_file_filter="Images (*.jpg *.jpeg *.png *.bmp)",
                    ui_info=GUIMessage("Select background image"),
                    validators=[validate_path],
                ),
                "backgroundOpacity": NumberOption(
                    default=50,
                    min=0,
                    max=100,
                    ui_info=GUIMessage(
                        "Set background opacity",
                        "A greater opacity yields a brighter background",
                    ),
                ),
                "backgroundBlur": NumberOption(
                    default=0,
                    min=0,
                    max=30,
                    ui_info=GUIMessage(
                        "Set background blur radius",
                        "A greater radius increases the blur effect",
                    ),
                ),
            },
            "Process": {
                "maxThreads": NumberOption(
                    default=1,
                    min=1,
                    max=None,
                    ui_group_parent=UIGroups.CLUSTERED,
                    ui_group="pu_threads",
                    ui_info=GUIMessage(
                        f"Maxmimum number of threads to run concurrently",
                        "Going beyond CPU core count will decrease performance for CPU-bound tasks",
                    ),
                ),
                "terminalSize": NumberOption(
                    default=600,
                    min=400,
                    max=None,
                    ui_group="pu_threads",
                    ui_info=GUIMessage(
                        "Terminal size", "Set the size of the terminal in pixels"
                    ),
                    ui_type=UITypes.SPINBOX,
                ),
            },
        }
