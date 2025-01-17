from qfluentwidgets import ToolTipFilter, ToolTipPosition, TextWrap
from PyQt6.QtCore import Qt, QObject, pyqtSignal, pyqtBoundSignal
from PyQt6.QtWidgets import QWidget

from abc import abstractmethod

from ....module.tools.types.gui_settings import AnySetting


class DisableWrapper:
    def __init__(
        self, is_disabled: bool, others_only: bool = False, save: bool = True
    ) -> None:
        self.is_disabled = is_disabled
        self.others_only = others_only
        self.save = save


class CardBase:
    notifyCard = pyqtSignal(tuple)  # notifyType: str, value: Any
    disableCard = pyqtSignal(DisableWrapper)
    disableChildren = pyqtSignal(DisableWrapper)

    def __init__(self, card_name: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._card_name = card_name
        self._tooltip_filters = {}  # type: dict[QWidget, ToolTipFilter]

    def _createToolTip(
        self,
        widget: QWidget | None,
        content: str | None,
        duration: int = 20000,
        show_delay: int = 300,
        position: ToolTipPosition = ToolTipPosition.TOP_LEFT,
    ) -> None:
        if content and widget:
            if widget in self._tooltip_filters:
                self._deleteToolTip(widget, self._tooltip_filters[widget])
            sh = widget.sizeHint().width()
            widget.setToolTip(TextWrap.wrap(content, max(sh // 2, 70), False)[0])
            widget.setToolTipDuration(duration)
            eventfilter = ToolTipFilter(
                parent=widget, showDelay=show_delay, position=position
            )
            widget.installEventFilter(eventfilter)
            self._tooltip_filters[widget] = eventfilter

    def _deleteToolTip(self, obj: QObject, tooltip: ToolTipFilter) -> None:
        obj.removeEventFilter(tooltip)
        filter = self._tooltip_filters.pop(obj)
        filter.deleteLater()

    def getCardName(self) -> str:
        return self._card_name

    def getDisableSignal(self) -> pyqtBoundSignal:
        return self.disableCard

    def getDisableChildrenSignal(self) -> pyqtBoundSignal:
        return self.disableChildren

    @abstractmethod
    def getOption(self) -> AnySetting: ...

    @abstractmethod
    def setDisableAll(self, wrapper: DisableWrapper) -> None: ...

    @abstractmethod
    def setOption(
        self,
        option: AnySetting,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignRight,
    ) -> None: ...


class ParentCardBase:
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    @abstractmethod
    def addChild(self, child: QWidget) -> None: ...


class ParentSettingCardBase(ParentCardBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def enableTightMode(self, is_tight: bool) -> tuple[int, int]:
        return self.card.enableTightMode(is_tight)
