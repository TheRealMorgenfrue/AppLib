from typing import Self, override

from ...logging import LoggingManager
from ..internal.core_args import CoreArgs
from ..runners.validators.generic_validator import validate_path
from ..runners.validators.logging_validator import validate_loglevel
from ..tools.template_utils.options import (
    ComboBoxOption,
    GUIMessage,
)
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
                    actions=[LoggingManager().set_level],
                    ui_info=GUIMessage(f"Set log level for {CoreArgs._core_app_name}"),
                    validators=[validate_loglevel],
                    values=LoggingManager.LogLevel._member_names_,
                )
            },
        }
