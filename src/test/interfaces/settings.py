from qfluentwidgets import FluentIcon as FIF
from PyQt6.QtWidgets import QWidget

from applib.app.components.cardstack import PivotCardStack
from applib.app.generators.card_generator import CardGenerator
from applib.module.config.app_config import AppConfig
from applib.module.config.internal.app_args import AppArgs
from applib.module.config.templates.app_template import AppTemplate
from applib.app.interfaces.settings_interface import CoreSettingsInterface
from applib.app.interfaces.settings_subinterface import CoreSettingsSubInterface


class TestSettingsInterface(CoreSettingsInterface):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self.addSubInterface(
            icon=FIF.AIRPLANE,
            title=AppArgs.app_name,
            widget=CoreSettingsSubInterface(
                config=AppConfig(),
                template=AppTemplate(),
                Generator=CardGenerator,
                CardStack=PivotCardStack,
            ),
        )
