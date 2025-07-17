from PyQt6.QtCore import QModelIndex, Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QListView, QMenu, QWidget
from qfluentwidgets import ListView, RoundMenu


class MenuListView(ListView):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._menu = None  # type: RoundMenu
        self.rightClickIndex = None  # type: QModelIndex
        self.setEditTriggers(QListView.EditTrigger.NoEditTriggers)

    def clear(self) -> None:
        self.rightClickIndex = None

    def setMenu(self, menu: QMenu):
        if self._menu:
            self._menu.deleteLater()
        menu.hide()
        self._menu = menu

    def mousePressEvent(self, e: QMouseEvent):
        super().mousePressEvent(e)
        if self._menu:
            if e.button() == Qt.MouseButton.RightButton:
                index = self.indexAt(e.position().toPoint())
                if index.isValid():
                    self.rightClickIndex = index
                    self._menu.exec(e.globalPosition().toPoint())
            else:
                self._menu.mousePressEvent(e)
