from test.modules.config.test_args import TestArgs
from typing import Self, override

from applib.app.common.auto_wrap import AutoTextWrap
from applib.module.configuration.internal.core_args import CoreArgs
from applib.module.configuration.runners.actions.theme_actions import (
    change_theme,
    change_theme_color,
)
from applib.module.configuration.runners.validators.app_validator import (
    validate_loglevel,
    validate_theme,
)
from applib.module.configuration.runners.validators.generic_validator import (
    validate_path,
)
from applib.module.configuration.templates.base_template import BaseTemplate
from applib.module.configuration.tools.template_utils.options import (
    ColorPickerOption,
    ComboBoxOption,
    FileSelectorOption,
    GUIMessage,
    GUIOption,
    NumberOption,
    TextEditOption,
)
from applib.module.configuration.tools.template_utils.template_enums import (
    UIFlags,
    UIGroups,
)
from applib.module.logging import LoggingManager


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
                "loglevel": ComboBoxOption(
                    default="INFO" if CoreArgs._core_is_release else "DEBUG",
                    actions=[LoggingManager().applib_logger().setLevel],
                    ui_info=GUIMessage(f"Set log level for {CoreArgs._core_app_name}"),
                    validators=[validate_loglevel],
                    values=TestArgs.main_loglevels,
                )
            },
            "Appearance": {
                "appTheme": ComboBoxOption(
                    default="System",
                    actions=[change_theme],
                    ui_info=GUIMessage("Set application theme"),
                    validators=[validate_theme],
                    values=TestArgs.main_themes,
                ),
                "appColor": ColorPickerOption(
                    default="#2abdc7",
                    actions=[change_theme_color],
                    ui_info=GUIMessage("Set application color"),
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
            "PixivUtil2": {
                "partialCompat": GUIOption(
                    default=False,
                    ui_flags=UIFlags.REQUIRES_RELOAD,
                    ui_group_parent=[
                        UIGroups.DESYNC_FALSE_CHILDREN,
                        UIGroups.UNDIRECTED_SYNC,
                    ],
                    ui_group="pu_compat",
                    ui_info=GUIMessage(
                        "Use partial compatibility mode",
                        AutoTextWrap.text_format(
                            f"""
                            <b>Recommended</b><br>Partial compatibility is preferred unless the meaning of
                            an existing key in NAMES's config has changed compared to
                            the config of {CoreArgs._core_app_name}.
                            """,
                        ),
                    ),
                ),
                "fullCompat": GUIOption(
                    default=False,
                    ui_flags=UIFlags.REQUIRES_RELOAD,
                    ui_group="pu_compat",
                    ui_info=GUIMessage(
                        "Use full compatibility mode",
                        AutoTextWrap.text_format(
                            f"""
                            <b>Not recommended</b><br>Use only if partial compatibility is insufficient and you know what you're doing.
                            Enabling full compatibility disables ALL safety measures against illegal or invalid values.
                            NAMES's config file will be used and displayed as-is.
                            """
                        ),
                    ),
                ),
            },
            "IrfanView": {
                "startIrfanView": GUIOption(
                    default=False,
                    ui_group_parent=UIGroups.DESYNC_TRUE_CHILDREN,
                    ui_group="downloadList_1",
                    ui_info=GUIMessage(
                        f"Start IrfanView with downloaded images when exiting NAME",
                        "This will create download-lists. Be sure to set IrfanView to load Unicode-Plugin on startup when there are unicode-named files",
                    ),
                ),
                "startIrfanSlide": GUIOption(
                    default=False,
                    ui_group_parent=UIGroups.DESYNC_TRUE_CHILDREN,
                    ui_group="downloadList_2",
                    ui_info=GUIMessage(
                        f"Start IrfanView Slideshow with downloaded images when exiting NAME",
                        "This will create download-lists. Be sure to set IrfanView to load Unicode-Plugin on startup when there are unicode-named files. Slideshow-options will be same as you have set in IrfanView before",
                    ),
                ),
                "createDownloadLists": GUIOption(
                    default=False,
                    ui_disable_self=False,
                    ui_group_parent=[
                        UIGroups.NESTED_CHILDREN,
                        UIGroups.DISABLE_CHILDREN,
                    ],
                    ui_group="downloadListFolder, downloadList_1, downloadList_2",
                    ui_info=GUIMessage(
                        "Automatically create download-lists",
                        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
                    ),
                ),
            },
            "Settings": {
                "downloadListDirectory": TextEditOption(
                    default="",
                    ui_group="downloadListFolder",
                    ui_invalid_input=GUIMessage("WIP", "This is a test"),
                    ui_info=GUIMessage(
                        "Folder for download lists",
                        "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt",
                    ),
                    validators=[validate_path],
                ),
                "ignore-config": GUIOption(
                    default=False,
                    ui_disable_self=False,
                    ui_group_parent=[UIGroups.CLUSTERED],
                    ui_group="config",
                    ui_info=GUIMessage(
                        "Don't load any more configuration files except those given to --config-locations",
                        "For backward compatibility, if this option is found inside the system configuration file, the user configuration is not loaded.",
                    ),
                ),
                "no-config-locations": GUIOption(
                    default=False,
                    ui_disable_self=False,
                    ui_group_parent=[
                        UIGroups.NESTED_CHILDREN,
                        UIGroups.DISABLE_CHILDREN,
                    ],
                    ui_group="config-locations, config",
                    ui_info=GUIMessage(
                        "Load custom configuration files",
                        "When disabled, ignore all previous --config-locations defined in the current configuration file",
                    ),
                ),
                "config-locations": FileSelectorOption(
                    default="",
                    ui_group="config-locations",
                    ui_info=GUIMessage(
                        "Location of the main configuration file",
                        "Either the path to the config or its containing directory",
                    ),
                ),
            },
        }
