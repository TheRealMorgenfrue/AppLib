from abc import abstractmethod
from typing import Optional, TypeAlias, Union, override

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QStackedWidget, QVBoxLayout, QWidget
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (
    FluentIconBase,
    Pivot,
    ScrollArea,
    SegmentedToolItem,
    SegmentedToolWidget,
    ToolTipFilter,
    ToolTipPosition,
    qrouter,
)

from ...module.logging import LoggingManager
from ...module.tools.types.gui_generators import AnyCardGenerator

# InQuad                        // Straight
# QEasingCurve.Type.InBack      // Bounce up
# QEasingCurve.Type.InOutBack   // Bounce up & down


# All QFluentWidgets' pivot classes are supported. Add as needed.
AnyPivot: TypeAlias = Pivot | SegmentedToolWidget


class CardStackBase(ScrollArea):
    def __init__(
        self,
        generator: AnyCardGenerator,
        Pivot: AnyPivot,
        pivotAlignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
        labeltext: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        try:
            self._logger = LoggingManager().applib_logger()
            super().__init__(parent)
            self._cards = generator.getCards()
            self._generatorDefaultGroup = generator.getDefaultGroup()
            self._view = QWidget(self)

            self.titleLabel = QLabel(self.tr(labeltext)) if labeltext else None
            self.vGeneralLayout = QVBoxLayout(self._view)
            self.hPivotLayout = QHBoxLayout()
            self.pivot = Pivot()  # type: AnyPivot
            self.pivotAlignment = pivotAlignment
            self.stackedWidget = QStackedWidget()
        except Exception:
            self.deleteLater()
            raise

    @abstractmethod
    def _addSubInterface(
        self, widget: QWidget, object_name: str, title: str, *args, **kwargs
    ) -> None:
        """
        This method is providing the interface for connecting a setting card group to the
        QStackedWidget and the Pivot.

        Parameters
        ----------
        widget : QWidget
            A setting card group created by a GUI Generator.

        object_name : str
            The object name that will be assigned to `widget`.

        title : str
            The title of the Pivot.
        """
        ...

    @abstractmethod
    def _addCardGroups(self) -> None:
        """
        This method is adding setting gard groups from the GUI Generator to the
        QStackedWidget using the method `_addSubInterface`.
        """
        ...

    def _initWidget(self) -> None:
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 0)
        self.setWidget(self._view)
        self.setWidgetResizable(True)
        self._setQss()

    def _setQss(self) -> None:
        self._view.setObjectName("view")
        if self.titleLabel:
            self.titleLabel.setObjectName("titleLabel")

    def _initLayout(self) -> None:
        self._addCardGroups()
        self.hPivotLayout.addWidget(self.pivot, alignment=self.pivotAlignment)

        if self.titleLabel:
            self.vGeneralLayout.addWidget(self.titleLabel)
        self.vGeneralLayout.addLayout(self.hPivotLayout)
        self.vGeneralLayout.addSpacing(10)
        self.vGeneralLayout.addWidget(self.stackedWidget)
        self.vGeneralLayout.setContentsMargins(0, 0, 0, 0)

        if self._generatorDefaultGroup:
            defaultGroup = self._generatorDefaultGroup
        else:
            self._logger.warning(
                f"No official default group defined for '{self.titleLabel.text() if self.titleLabel else None}'"
            )
            if self._cards:
                defaultGroup = self._cards[0]
            else:
                self._logger.error(
                    "List has no card groups defined. Substitution impossible. Nothing will be shown"
                )
                defaultGroup = None

        if defaultGroup is not None:
            # Set Group shown on application start
            self.stackedWidget.setCurrentWidget(defaultGroup)
            # Set Group marked as selected on application start
            self.pivot.setCurrentItem(defaultGroup.objectName())
            # Set navigation history to default Group
            qrouter.setDefaultRouteKey(self.stackedWidget, defaultGroup.objectName())

    def _connectSignalToSlot(self) -> None:
        self.stackedWidget.currentChanged.connect(self._onCurrentIndexChanged)

    def _onCurrentIndexChanged(self, index) -> None:
        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())
        qrouter.push(self.stackedWidget, widget.objectName())


class PivotCardStack(CardStackBase):
    def __init__(
        self,
        generator: AnyCardGenerator,
        labeltext: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Create a standard settings interface.

        It is composed of a Pivot and a QStackedWidget.
        Uses widgets created by `generator` as content.

        Parameters
        ----------
        generator : AnyCardGenerator
            The GUI generator which supplies the setting cards displayed.

        labeltext : str, optional
            The title of the CardStack.
            By default None.

        parent : QWidget, optional
            The parent widget of the CardStack.
            By default None.
        """
        try:
            super().__init__(
                generator=generator, Pivot=Pivot, labeltext=labeltext, parent=parent
            )
            self._initWidget()
            self._initLayout()
            self._connectSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    @override
    def _addCardGroups(self) -> None:
        for group in self._cards:
            name = group.getTitleLabel().text()
            self._addSubInterface(widget=group, objectName=name, title=name)

    @override
    def _addSubInterface(self, widget: QWidget, objectName: str, title: str) -> None:
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(
            routeKey=objectName,
            text=title,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget),
            icon=None,
        )


class SegmentedPivotCardStack(CardStackBase):
    def __init__(
        self,
        generator: AnyCardGenerator,
        icons: dict[str, Union[str, QIcon, FluentIconBase]],
        labeltext: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Create a standard settings interface.

        It is composed of a Segmented Pivot, which uses the supplied icon list, and a QStackedWidget.
        Uses widgets created by the generator as content.

        Parameters
        ----------
        generator : AnyCardGenerator
            The widget generator which supplies the content widgets displayed.

        icons : list[str | QIcon | FluentIconBase]
            The icons shown in the Pivot for each card category.

        labeltext : str, optional
            The title of the CardStack, by default None.

        parent : QWidget, optional
            The parent widget of the CardStack, by default None.
        """
        try:
            super().__init__(
                generator=generator,
                Pivot=Pivot,
                pivotAlignment=Qt.AlignmentFlag.AlignHCenter,
                labeltext=labeltext,
                parent=parent,
            )
            self.icons = icons

            self._initWidget()
            self._initLayout()
            self._connectSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    @override
    def _addCardGroups(self) -> None:
        for group in self._cards:
            name = group.getTitleLabel().text()
            self._addSubInterface(
                widget=group,
                object_name=name,
                title=name,
                icon=self.icons.get(name.lower(), FIF.CANCEL_MEDIUM),
            )

    @override
    def _addSubInterface(
        self,
        widget: QWidget,
        object_name: str,
        title: str,
        icon: Optional[Union[str, QIcon, FluentIconBase]],
    ):
        widget.setObjectName(object_name)
        self.stackedWidget.addWidget(widget)

        if icon is None:
            pivotItem = SegmentedToolItem()
        else:
            pivotItem = SegmentedToolItem(icon)
        pivotItem.setToolTip(title)
        pivotItem.setToolTipDuration(5000)
        pivotItem.installEventFilter(
            ToolTipFilter(parent=pivotItem, showDelay=100, position=ToolTipPosition.TOP)
        )
        self.pivot.addWidget(
            routeKey=object_name,
            widget=pivotItem,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget),
        )
