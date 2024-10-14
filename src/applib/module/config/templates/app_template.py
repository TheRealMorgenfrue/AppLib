from typing import Self, override

from ..internal.app_args import AppArgs
from ..templates.template_base import BaseTemplate
from ..templates.template_enums import UIGroups, UITypes
from ..validators import validateLoglevel, validateTheme
from ..validators.generic_validator import validatePath
from ...tools.types.general import NestedDict


class AppTemplate(BaseTemplate):
    _instance = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._created = False
        return cls._instance

    def __init__(self) -> None:
        if not self._created:
            super().__init__(
                template_name=AppArgs.app_template_name,
                template=self._createTemplate(),
                icons=None,
            )
            self._created = True

    @override
    def _createTemplate(self) -> NestedDict:
        return {
            "General": {
                "loglevel": {
                    "ui_type": UITypes.COMBOBOX,
                    "ui_title": f"Set log level for {AppArgs.app_name}",
                    "default": "INFO" if AppArgs.is_release else "DEBUG",
                    "values": AppArgs.template_loglevels,
                    "validators": [validateLoglevel],
                }
            },
            "Appearance": {
                "appTheme": {
                    "ui_type": UITypes.COMBOBOX,
                    "ui_title": "Set application theme",
                    "default": "System",
                    "values": AppArgs.template_themes,
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
                    "default": 3,
                    "min": 1,
                    "max": None,
                    "ui_group_parent": UIGroups.CLUSTERED,
                    "ui_group": "pu_threads",
                },
                "terminalSize": {
                    "ui_title": "Terminal size",
                    "ui_desc": "Set the size of the terminal in pixels",
                    "default": 400,
                    "min": 400,
                    "max": None,
                    "ui_type": UITypes.SPINBOX,
                    "ui_group": "pu_threads",
                },
            },
        }
