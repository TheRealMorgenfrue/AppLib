from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QLabel, QSizePolicy, QWidget


class FluentLabel(QLabel):
    def __init__(
        self,
        text: str | None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(text, parent)
        self.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding
        )

    def sizeHint(self) -> QSize:
        self.updateGeometry()
        if self.isHidden() or not self.text():
            return QSize(0, 0)

        # Compute width
        p = self.parentWidget()
        w = p.width() if p else self.fontMetrics().horizontalAdvance(self.text())

        # Compute height
        www = (
            self.fontMetrics()
            .boundingRect(self.rect(), Qt.TextFlag.TextWordWrap, self.text())
            .width()
        )
        h = self.heightForWidth(www)
        return QSize(w, h)
