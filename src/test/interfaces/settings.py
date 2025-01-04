from qfluentwidgets import FluentIcon as FIF
from PyQt6.QtWidgets import QWidget

from applib.app.components.cardstack import PivotCardStack
from applib.app.generators.card_generator import CardGenerator
from applib.module.config.core_config import CoreConfig
from applib.module.config.internal.core_args import CoreArgs
from applib.module.config.templates.core_template import CoreTemplate
from applib.app.interfaces.settings_interface import CoreSettingsInterface
from applib.app.interfaces.settings_subinterface import CoreSettingsSubInterface


class TestSettingsInterface(CoreSettingsInterface):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self.addSubInterface(
            icon=FIF.AIRPLANE,
            title=CoreArgs._core_app_name,
            widget=CoreSettingsSubInterface(
                config=CoreConfig(),
                template=CoreTemplate(),
                Generator=CardGenerator,
                CardStack=PivotCardStack,
                title=self.tr(f"{CoreConfig().getConfigName()} Settings"),
            ),
        )
