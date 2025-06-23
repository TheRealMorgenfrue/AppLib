from modules.config.templates.test_template import TestTemplate
from modules.config.test_config import TestConfig
from PyQt6.QtWidgets import QWidget
from qfluentwidgets import FluentIcon as FIF

from applib.app.components.cardstack import PivotCardStack
from applib.app.generators.card_generator import CardGenerator
from applib.app.interfaces.settings_interface import CoreSettingsInterface
from applib.app.interfaces.settings_subinterface import CoreSettingsSubInterface
from applib.module.configuration.internal.core_args import CoreArgs


class TestSettingsInterface(CoreSettingsInterface):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self.addSubInterface(
            icon=FIF.AIRPLANE,
            title=CoreArgs._core_app_name,
            widget=CoreSettingsSubInterface(
                config=TestConfig(),
                template=TestTemplate(),
                Generator=CardGenerator,
                CardStack=PivotCardStack,
            ),
        )
