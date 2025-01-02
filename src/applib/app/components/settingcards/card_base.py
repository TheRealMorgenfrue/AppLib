from abc import abstractmethod
from PyQt6.QtCore import Qt, pyqtSignal, pyqtBoundSignal
from PyQt6.QtWidgets import QWidget

from ....module.tools.types.gui_settings import AnySetting


class DisableWrapper:
    def __init__(
        self, is_disabled: bool, othersOnly: bool = False, save: bool = True
    ) -> None:
        self.is_disabled = is_disabled
        self.othersOnly = othersOnly
        self.save = save


class CardBase:
    notifyCard = pyqtSignal(tuple)  # notifyType: str, value: Any
    disableCard = pyqtSignal(DisableWrapper)
    disableChildren = pyqtSignal(DisableWrapper)

    def __init__(self, cardName: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._cardName = cardName

    def getCardName(self) -> str:
        return self._cardName

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
