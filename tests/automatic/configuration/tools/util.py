from typing import Self, override

from applib.module.configuration.runners.actions.theme_actions import change_theme_color
from applib.module.configuration.runners.validators.generic_validator import (
    validate_path,
)
from applib.module.configuration.templates.base_template import BaseTemplate
from applib.module.configuration.tools.template_utils.options import (
    ColorPickerOption,
    FileSelectorOption,
    GUIMessage,
    TextEditOption,
)
from applib.module.logging import LoggingManager
from applib.module.logging.logger_utils import create_main_logger


def setup_logger():
    logger = LoggingManager()
    create_main_logger()
    return logger


def validate_testing(val: str) -> str:
    return val


class AutoTestingTemplate(BaseTemplate):
    _instance = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._created = False
        return cls._instance

    def __init__(self) -> None:
        if not self._created:
            super().__init__(
                name="TestT",
                template=self._create_template(),
                icons=None,
            )
            self._created = True

    @override
    def _create_template(self) -> dict:
        return {
            "Appearance": {
                "appColor": ColorPickerOption(
                    default="#2abdc7",
                    actions=[validate_testing, change_theme_color],
                    ui_info=GUIMessage("Set application color"),
                ),
                "appBackground": FileSelectorOption(
                    default="",
                    ui_file_filter="Images (*.jpg *.jpeg *.png *.bmp)",
                    ui_info=GUIMessage("Select background image"),
                    validators=[validate_path, validate_testing, validate_testing],
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
                    validators=[validate_path, validate_testing],
                )
            },
        }
