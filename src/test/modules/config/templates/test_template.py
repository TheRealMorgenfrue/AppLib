from test.modules.config.test_args import TestArgs
from typing import Self, override

from qfluentwidgets import setThemeColor

from applib.app.common.auto_wrap import AutoTextWrap
from applib.module.configuration.internal.core_args import CoreArgs
from applib.module.configuration.templates.base_template import BaseTemplate
from applib.module.configuration.tools.template_options.actions import change_theme
from applib.module.configuration.tools.template_options.template_enums import (
    UIFlags,
    UIGroups,
    UITypes,
)
from applib.module.configuration.validators.app_validator import (
    validate_loglevel,
    validate_theme,
)
from applib.module.configuration.validators.generic_validator import validate_path


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
                name=TestArgs.main_template_name,
                template=self._create_template(),
                icons=None,
            )
            self._created = True

    @override
    def _create_template(self) -> dict:
        return {
            "General": {
                "loglevel": {
                    "ui_type": UITypes.COMBOBOX,
                    "ui_title": f"Set log level for {CoreArgs._core_app_name}",
                    "default": "INFO" if CoreArgs._core_is_release else "DEBUG",
                    "values": TestArgs.main_loglevels,
                    "validators": [validate_loglevel],
                    "actions": [self._logger.setLevel],
                }
            },
            "Appearance": {
                "appTheme": {
                    "ui_type": UITypes.COMBOBOX,
                    "ui_title": "Set application theme",
                    "default": "System",
                    "values": TestArgs.main_themes,
                    "validators": [validate_theme],
                    "actions": [change_theme],
                },
                "appColor": {
                    "ui_type": UITypes.COLOR_PICKER,
                    "ui_title": "Set application color",
                    "default": "#2abdc7",
                    "actions": [lambda color: setThemeColor(color, lazy=True)],
                },
                "appBackground": {
                    "ui_type": UITypes.FILE_SELECTION,
                    "ui_title": "Select background image",
                    "ui_file_filter": "Images (*.jpg *.jpeg *.png *.bmp)",
                    "default": "",
                    "validators": [validate_path],
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
                    "ui_group_parent": UIGroups.DESYNC_TRUE_CHILDREN,
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
                    "ui_desc": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
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
                    "ui_title": "Folder for download lists",
                    "ui_desc": "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt",
                    "ui_invalidmsg": ("WIP", "This is a test"),
                    "default": "",
                    "validators": [validate_path],
                    "ui_group": "downloadListFolder",
                },
            },
        }
