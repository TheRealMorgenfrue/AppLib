from typing import Self, override

from ..internal.core_args import CoreArgs
from .base_template import BaseTemplate
from .template_enums import UIGroups, UITypes
from ..validators import validateLoglevel, validateTheme
from ..validators.generic_validator import validatePath


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
                template=self._createTemplate(),
                icons=None,
            )
            self._created = True

    @override
    def _createTemplate(self) -> dict:
        return {
            "General": {
                "loglevel": {
                    "ui_type": UITypes.COMBOBOX,
                    "ui_title": f"Set log level for {CoreArgs._core_app_name}",
                    "default": "INFO" if CoreArgs._core_is_release else "DEBUG",
                    "values": CoreArgs._core_template_loglevels,
                    "validators": [validateLoglevel],
                }
            },
            "Appearance": {
                "appTheme": {
                    "ui_type": UITypes.COMBOBOX,
                    "ui_title": "Set application theme",
                    "default": "System",
                    "values": CoreArgs._core_template_themes,
                    "validators": [validateTheme],
                },
                "appColor": {
                    "ui_type": UITypes.COLOR_PICKER,
                    "ui_title": "Set application color",
                    "default": "#2abdc7",
                },
                "appBackground": {
                    "ui_type": UITypes.FILE_SELECTION,
                    "ui_title": "Select background image",
                    "ui_file_filter": "Images (*.jpg *.jpeg *.png *.bmp)",
                    "default": "",
                    "validators": [validatePath],
                },
                "backgroundOpacity": {
                    "ui_title": "Set background opacity",
                    "ui_desc": "A greater opacity yields a brighter background",
                    "default": 50,
                    "min": 0,
                    "max": 100,
                },
                "backgroundBlur": {
                    "ui_title": "Set background blur radius",
                    "ui_desc": "A greater radius increases the blur effect",
                    "default": 0,
                    "min": 0,
                    "max": 30,
                },
            },
            "Process": {
                "maxThreads": {
                    "ui_title": f"Maxmimum number of threads to run concurrently",
                    "ui_desc": "Going beyond CPU core count will hurt performance for CPU-bound tasks",
                    "default": 1,
                    "min": 1,
                    "max": None,
                    "ui_group_parent": UIGroups.CLUSTERED,
                    "ui_group": "pu_threads",
                },
                "terminalSize": {
                    "ui_title": "Terminal size",
                    "ui_desc": "Set the size of the terminal in pixels",
                    "default": 600,
                    "min": 400,
                    "max": None,
                    "ui_type": UITypes.SPINBOX,
                    "ui_group": "pu_threads",
                },
            },
        }
