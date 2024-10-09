from typing import Self, override

from app.common.auto_wrap import AutoTextWrap
from module.config.internal.app_args import AppArgs
from module.config.internal.names import ModuleNames, TemplateNames
from module.config.templates.template_base import BaseTemplate
from module.config.templates.template_enums import UIFlags, UIGroups, UITypes
from module.config.validators import validateLoglevel, validateTheme
from module.config.validators.generic_validator import validatePath
from module.tools.types.general import NestedDict


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
                template_name=TemplateNames.app_template_name,
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
                    "ui_title": f"Set log level for {ModuleNames.app_name}",
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
            "PixivUtil2": {
                "maxThreads": {
                    "ui_title": f"Maxmimum number of {ModuleNames.pu_name} processes to run concurrently",
                    "ui_desc": "Going beyond 4 is not recommended as it substantially increases the chance of Pixiv blocking your IP address",
                    "default": 3,
                    "min": 1,
                    "max": 12,
                    "ui_group_parent": UIGroups.CLUSTERED,
                    "ui_group": "pu_threads",
                },
                "idsPerProcess": {
                    "ui_title": "Number of Pixiv IDs to download per process",
                    "ui_desc": "Going beyond 10 is not recommended",
                    "default": 5,
                    "min": 1,
                    "max": 20,
                    "ui_group": "pu_threads",
                },
                "terminalSize": {
                    "ui_title": "Terminal size",
                    "ui_desc": "Set the size of the terminal in pixels",
                    "default": 400,
                    "min": 400,
                    "max": 4000,
                    "ui_type": UITypes.SPINBOX,
                    "ui_group": "pu_threads",
                },
                "partialCompat": {
                    "ui_title": "Use partial compatibility mode",
                    "ui_desc": AutoTextWrap.text_format(
                        f"""
                        <b>Recommended</b><br>Partial compatibility is suitable for all cases except if
                        the semantics (meaning) of an existing key in {ModuleNames.pu_name}'s config has changed compared to
                        the config of {ModuleNames.app_name}.
                        """,
                    ),
                    "default": False,
                    "ui_group_parent": UIGroups.DESYNC_TRUE_CHILDREN,
                    "ui_group": "pu_partialCompat, pu_fullCompat",
                    "ui_flags": UIFlags.REQUIRES_RELOAD,
                },
                "fullCompat": {
                    "ui_title": "Use full compatibility mode",
                    "ui_desc": AutoTextWrap.text_format(
                        f"""
                        <b>Not recommended</b><br>Use only if partial compatibility is insufficient and you know what you're doing.
                        Enabling full compatibility disables ALL safety measures against illegal or invalid values.
                        {ModuleNames.pu_name}'s config file will be used and displayed as-is.
                        """
                    ),
                    "default": False,
                    "ui_group": "pu_partialCompat",
                    "ui_flags": UIFlags.REQUIRES_RELOAD,
                },
            },
        }
