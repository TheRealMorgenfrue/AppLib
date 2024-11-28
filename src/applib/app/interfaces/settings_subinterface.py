from qfluentwidgets import ScrollArea
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from typing import Optional

from ..common.core_stylesheet import CoreStyleSheet

from ...module.tools.types.config import AnyConfig
from ...module.tools.types.templates import AnyTemplate
from ...module.tools.types.gui_generators import AnyCardGenerator
from ...module.tools.types.gui_cardstacks import AnyCardStack


class CoreSettingsSubInterface(ScrollArea):
    def __init__(
        self,
        config: AnyConfig,
        template: AnyTemplate,
        Generator: AnyCardGenerator,
        CardStack: AnyCardStack,
        parent: Optional[QWidget] = None,
    ):
        """
        Create a default settings panel for a `config`/`template` duo, where GUI components
        are created by `Generator` and laid out with `CardStack`.

        Parameters
        ----------
        config : AnyConfig
            The GUI is connected to `config`, which is updated when key/value pairs in the GUI change.

        template : AnyTemplate
            Specification which defines the creation of GUI elements.

        Generator : AnyCardGenerator
            Creates the GUI elements, by following the `template` specification, in a style defined by the particular `Generator`.
            NOTE: Must be a class reference.

        CardStack : AnyCardStack
            Lays out GUI elements using the layout style of the particular `CardStack`.
            NOTE: Must be a class reference.

        parent : QWidget, optional
            The parent widget of the subinterface.
            By default None.
        """
        try:
            super().__init__(parent)
            self._config = config
            self._template = template
            self._Generator = Generator
            self._CardStack = CardStack

            self._view = QWidget(self)
            self.vGeneralLayout = QVBoxLayout(self._view)

            self._initWidget()
            self._initLayout()
        except Exception:
            self.deleteLater()
            raise

    def _initWidget(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 0)
        self.setWidget(self._view)
        self.setWidgetResizable(True)
        self._setQss()

    def _setQss(self):
        self._view.setObjectName("view")
        self.setObjectName("settingsSubInterface")
        CoreStyleSheet.SETTINGS_SUBINTERFACE.apply(self)

    def _initLayout(self) -> None:
        generator = self._Generator(
            config=self._config, template=self._template, parent=self
        )
        card_stack = self._CardStack(
            generator=generator,
            labeltext=self.tr(f"{self._config.getConfigName()} Settings"),
            parent=self,
        )
        CoreStyleSheet.SETTINGS_SUBINTERFACE.apply(card_stack)
        self.vGeneralLayout.addWidget(card_stack)
