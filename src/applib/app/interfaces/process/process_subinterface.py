from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import ScrollArea

from ....module.tools.types.config import AnyConfig
from ....module.tools.types.templates import AnyTemplate
from ...common.core_stylesheet import CoreStyleSheet
from ...components.progresscards.progress_ring_card import ProgressRingCard
from ...generators.cardwidget_generator import CardWidgetGenerator


class CoreProcessSettings(ScrollArea):
    def __init__(
        self, config: AnyConfig, template: AnyTemplate, parent: Optional[QWidget] = None
    ) -> None:
        """
        The default process settings panel for the process interface.

        Parameters
        ----------
        config : AnyConfig
            The GUI is connected to `config`, which is updated when key/value pairs in the GUI change.

        template : AnyTemplate
            Specification which defines the creation of GUI elements.

        parent : Optional[QWidget], optional
            The parent widget of the process settings panel.
            By default None.
        """
        super().__init__(parent)
        self._view = QWidget(self)
        self._config = config
        self._template = template
        self.vBoxLayout = QVBoxLayout(self._view)

        self._initWidget()
        self._initLayout()

    def _initWidget(self) -> None:
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 0)
        self.setWidget(self._view)
        self.setWidgetResizable(True)
        self._setQss()

    def _setQss(self) -> None:
        self.setObjectName("processSettings")
        self._view.setObjectName("view")
        CoreStyleSheet.PROCESS_INTERFACE.apply(self)

    def _initLayout(self) -> None:
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)

        generator = CardWidgetGenerator(
            config=self._config,
            template=self._template,
            is_tight=True,
            parent=self,
        )
        for card in generator.getCards():
            self.vBoxLayout.addWidget(card)


class CoreProcessStatus(ScrollArea):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        The default process status card.

        Parameters
        ----------
        parent : Optional[QWidget], optional
            The parent widget of the process status card.
            By default None.
        """
        super().__init__(parent)
        self._view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self._view)
        self.progress_ring_card = ProgressRingCard(self.tr("Process Status"))

        self._initWidget()
        self._initLayout()

    def _initWidget(self) -> None:
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 0)
        self.setWidget(self._view)
        self.setWidgetResizable(True)
        self._setQss()

    def _setQss(self) -> None:
        self.setObjectName("processStatus")
        self._view.setObjectName("view")
        CoreStyleSheet.PROCESS_INTERFACE.apply(self)

    def _initLayout(self) -> None:
        self.vBoxLayout.setContentsMargins(0, 20, 0, 0)
        self.vBoxLayout.addWidget(
            self.progress_ring_card,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter,
        )


class ProcessSubinterface(QWidget):
    def __init__(
        self, config: AnyConfig, template: AnyTemplate, parent: Optional[QWidget] = None
    ) -> None:
        """
        The default subinterface for the process interface.

        Contains a process status card and a process settings panel.

        Parameters
        ----------
        config : AnyConfig
            The GUI is connected to `config`, which is updated when key/value pairs in the GUI change.
            Used by the process settings panel.

        template : AnyTemplate
            Specification which defines the creation of GUI elements.
            Used by the process settings panel.

        parent : Optional[QWidget], optional
            The parent widget of the process subinterface.
            By default None.
        """
        super().__init__(parent)
        self.vBoxLayout = QVBoxLayout(self)

        self.process_status = CoreProcessStatus()
        self.process_settings = CoreProcessSettings(config=config, template=template)

        self._initLayout()

    def _initLayout(self) -> None:
        # self.setMinimumWidth(400)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(10)
        self.vBoxLayout.addWidget(self.process_status, 2)
        self.vBoxLayout.addWidget(self.process_settings, 3)

    def getProgressCard(self) -> ProgressRingCard:
        return self.process_status.progress_ring_card
