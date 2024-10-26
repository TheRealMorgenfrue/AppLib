from typing import Optional
from PyQt6.QtCore import Qt, QSize, QRect

from PyQt6.QtGui import QResizeEvent
from PyQt6.QtWidgets import (
    QLabel,
    QWidget,
    QStyle,
)

from module.logging import logger


class FluentLabel(QLabel):
    test_logger = logger

    def __init__(
        self,
        text: Optional[str],
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(text, parent)

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

    # def resizeEvent(self, e: QResizeEvent | None) -> None:
    #     super().resizeEvent(e)
    #     self.test_logger.debug(f"{f"{self.text()[0:8]} | " if self.text() else ""}old: {e.oldSize()} | new: {e.size()}")

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
        # print(f"{self.text()[0:8]} | w: {w} | h: {h} | www: {www}")
        return QSize(w, h)
