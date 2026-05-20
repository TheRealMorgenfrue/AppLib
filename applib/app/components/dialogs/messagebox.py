from PyQt6.QtWidgets import QWidget

from .messagebox_base import MessageBoxBase


class TextMessageBox(MessageBoxBase):
    def __init__(
        self,
        title: str,
        content: str,
        yesButtonText: str | None = None,
        noButtonText: str | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(
            title=title,
            content=content,
            yesButtonText=yesButtonText,
            noButtonText=noButtonText,
            parent=parent,
        )
