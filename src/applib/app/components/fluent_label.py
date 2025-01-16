from typing import Optional
from PyQt6.QtCore import Qt, QSize, QRect
from PyQt6.QtWidgets import QLabel, QWidget, QStyle, QSizePolicy

from ...module.logging import AppLibLogger


class FluentLabel(QLabel):
    test_logger = AppLibLogger().getLogger()

    def __init__(
        self,
        text: Optional[str],
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(text, parent)
        self.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding
        )

    def _documentRect(self) -> QRect:
        """
        Compute document rect which sometimes is more accurate than
        boundingRect() (which has a tendency to underestimate the rect)

        Code adapted from 'QLabelPrivate::documentRect()' at:
          https://code.qt.io/cgit/qt/qtbase.git/tree/src/widgets/widgets/qlabel.cpp

        Returns
        -------
        QRect
            The document rect where the label's text is drawn
        """
        cr = self.contentsRect()
        margin = self.margin()
        cr.adjust(margin, margin, -margin, -margin)
        align = QStyle.visualAlignment(self.layoutDirection(), self.alignment())
        indent = self.indent()
        if indent < 0 and self.frameWidth():  # No indent, but we do have a frame
            indent = self.fontMetrics().horizontalAdvance("x") / 2 - margin
        if indent > 0:
            if align | Qt.AlignmentFlag.AlignLeft:
                cr.setLeft(cr.left() + indent)
            if align | Qt.AlignmentFlag.AlignRight:
                cr.setRight(cr.right() - indent)
            if align | Qt.AlignmentFlag.AlignTop:
                cr.setTop(cr.top() + indent)
            if align | Qt.AlignmentFlag.AlignBottom:
                cr.setBottom(cr.bottom() - indent)
        return cr

    def sizeHint(self) -> QSize:
        self.updateGeometry()
        if self.isHidden() or not self.text():
            return QSize(0, 0)

        # Compute width
        p = self.parentWidget()
        if p:
            w = p.width()
        else:
            shW = super().sizeHint().width()
            rctW = self.fontMetrics().boundingRect(self.text()).width()
            docW = self._documentRect().width()
            w = max(rctW, docW, shW)

        # Compute height
        www = (
            self.fontMetrics()
            .boundingRect(self.rect(), Qt.TextFlag.TextWordWrap, self.text())
            .width()
        )
        h = self.heightForWidth(www)
        return QSize(w, h)
