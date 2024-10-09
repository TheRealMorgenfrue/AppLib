from PyQt6.QtWidgets import QWidget

from typing import Optional

from app.components.dialogs.messagebox_base import MessageBoxBase


class TextMessageBox(MessageBoxBase):
    def __init__(
        self,
        title: str,
        content: str,
        yesButtonText: Optional[str] = None,
        noButtonText: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(
            title=title,
            content=content,
            yesButtonText=yesButtonText,
            noButtonText=noButtonText,
            parent=parent,
        )
