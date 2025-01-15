from typing import Self, override

from applib.app.common.auto_wrap import AutoTextWrap
from applib.module.config.internal.core_args import CoreArgs
from applib.module.config.templates.base_template import BaseTemplate
from applib.module.config.templates.template_enums import UIFlags, UIGroups, UITypes
from applib.module.config.validators.app_validator import (
    validateLoglevel,
    validateTheme,
)
from applib.module.config.validators.generic_validator import validatePath
from test.modules.config.test_args import TestArgs


class TestTemplate(BaseTemplate):
    _instance = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._created = False
        return cls._instance

    def __init__(self) -> None:
        if not self._created:
            super().__init__(
                template_name=TestArgs.main_template_name,
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
                    "values": TestArgs.main_loglevels,
                    "validators": [validateLoglevel],
                }
            },
            "Appearance": {
                "appTheme": {
                    "ui_type": UITypes.COMBOBOX,
                    "ui_title": "Set application theme",
                    "default": "System",
                    "values": TestArgs.main_themes,
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
                "partialCompat": {
                    "ui_title": "Use partial compatibility mode",
                    "ui_desc": AutoTextWrap.text_format(
                        f"""
                        <b>Recommended</b><br>Partial compatibility is preferred unless the meaning of
                        an existing key in NAMES's config has changed compared to
                        the config of {CoreArgs._core_app_name}.
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
                        NAMES's config file will be used and displayed as-is.
                        """
                    ),
                    "default": False,
                    "ui_group": "pu_fullCompat, pu_partialCompat",
                    "ui_flags": UIFlags.REQUIRES_RELOAD,
                },
            },
            "IrfanView": {
                "startIrfanView": {
                    "ui_title": f"Start IrfanView with downloaded images when exiting NAME",
                    "ui_desc": "This will create download-lists. Be sure to set IrfanView to load Unicode-Plugin on startup when there are unicode-named files",
                    "default": False,
                    "ui_group_parent": UIGroups.DESYNC_TRUE_CHILDREN,
                    "ui_group": "downloadList_1",
                },
                "startIrfanSlide": {
                    "ui_title": f"Start IrfanView Slideshow with downloaded images when exiting NAME",
                    "ui_desc": "This will create download-lists. Be sure to set IrfanView to load Unicode-Plugin on startup when there are unicode-named files. Slideshow-options will be same as you have set in IrfanView before",
                    "default": False,
                    "ui_group_parent": UIGroups.DESYNC_TRUE_CHILDREN,
                    "ui_group": "downloadList_2",
                },
                "createDownloadLists": {
                    "ui_title": "Automatically create download-lists",
                    "default": False,
                    "ui_group_parent": [
                        UIGroups.NESTED_CHILDREN,
                        UIGroups.DISABLE_CHILDREN,
                    ],
                    "ui_group": "downloadListFolder, downloadList_1, downloadList_2",
                    "ui_disable_self": False,
                },
            },
            "Settings": {
                "downloadListDirectory": {
                    "ui_title": "Folder for download lists.",
                    "ui_invalidmsg": {"title": "", "desc": ""},
                    "default": "",
                    "validators": [validatePath],
                    "ui_group": "downloadListFolder",
                },
            },
            "Processor": {
                "maxThreads": {
                    "ui_title": f"Maxmimum number of NAME processes to run concurrently",
                    "ui_desc": "Going beyond 4 is not recommended as it substantially increases the chance of NAME blocking your IP address",
                    "default": 3,
                    "min": 1,
                    "max": 12,
                    "ui_group_parent": UIGroups.CLUSTERED,
                    "ui_group": "pu_threads",
                },
                "idsPerProcess": {
                    "ui_title": "Number of NAME IDs to download per process",
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
            },
        }
