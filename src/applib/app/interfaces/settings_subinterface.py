from typing import Literal, Optional, Union

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import FluentIconBase, ScrollArea

from ...module.tools.types.config import AnyConfig
from ...module.tools.types.gui_cardstacks import AnyCardStack
from ...module.tools.types.gui_generators import AnyCardGenerator
from ...module.tools.types.templates import AnyTemplate
from ..common.core_stylesheet import CoreStyleSheet


class CoreSettingsSubInterface(ScrollArea):
    def __init__(
        self,
        config: AnyConfig,
        template: AnyTemplate,
        Generator: AnyCardGenerator,
        CardStack: AnyCardStack,
        title: str | Literal["DEFAULT"] | None = "DEFAULT",
        icons: dict[str, Union[str, QIcon, FluentIconBase]] = None,
        parent: Optional[QWidget] = None,
        **generator_kwargs,
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

        title : str
            The display title of the interface.
            By default `DEFAULT`, which sets the title to `f"{config.name} Settings"`.

        icons : dict[str, Union[str, QIcon, FluentIconBase]]
            The icons shown in the pivot for each GUI element section, if supported by the `CardStack`.
            Must be a dict mapping a GUI element section, as defined in `template`, to an icon.
            By default `None`.

        parent : QWidget, optional
            The parent widget of the subinterface.
            By default `None`.

        generator_kwargs : dict
            Additional keyword arguments supplied to `Generator`.
            See the documentation of `Generator` for applicable kwargs.
        """
        try:
            super().__init__(parent)
            self._config = config
            self._template = template
            self._Generator = Generator
            self._CardStack = CardStack
            self._icons = icons
            self._title = title

            if "parent" not in generator_kwargs:
                generator_kwargs["parent"] = self
            self._generator_kwargs = generator_kwargs

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
            config=self._config, template=self._template, **self._generator_kwargs
        )

        cardstack_kwargs = {}
        if self._icons:
            cardstack_kwargs = {"icons": self._icons}

        card_stack = self._CardStack(
            generator=generator,
            labeltext=(
                f"{self._config.name} Settings"
                if self._title == "DEFAULT"
                else self._title
            ),
            parent=self,
            **cardstack_kwargs,
        )
        CoreStyleSheet.SETTINGS_SUBINTERFACE.apply(card_stack)
        self.vGeneralLayout.addWidget(card_stack)
