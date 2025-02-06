import os
from typing import Any, Optional

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QBrush, QPainter, QPainterPath, QPixmap
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import FluentIcon, ScrollArea

from ...module.configuration.internal.core_args import CoreArgs
from ...module.tools.types.config import AnyConfig
from ...module.tools.types.general import StrPath
from ..common.core_signalbus import core_signalbus
from ..common.core_stylesheet import CoreStyleSheet
from ..components.link_card import LinkCardView


class BannerWidget(QWidget):
    def __init__(
        self,
        main_config: AnyConfig,
        banner_path: StrPath,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent=parent)
        self.main_config = main_config
        self.is_background_active = bool(self.main_config.get_value("appBackground"))
        self.show_banner = (
            not self.is_background_active
            or int(self.main_config.get_value("backgroundOpacity")) == 0
        )

        self.vBoxLayout = QVBoxLayout(self)
        self.galleryLabel = QLabel(
            f"{CoreArgs._core_app_name}\nv{CoreArgs._core_app_version}", self
        )

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(Qt.GlobalColor.black)
        shadow.setOffset(1.2, 1.2)

        self.galleryLabel.setGraphicsEffect(shadow)
        self.galleryLabel.setObjectName("galleryLabel")

        self.banner = QPixmap(banner_path)

        self.linkCardView = LinkCardView(self)
        self.linkCardView.setContentsMargins(0, 0, 0, 36)

        # Create a horizontal layout for the linkCardView with bottom alignment and margin
        linkCardLayout = QHBoxLayout()
        linkCardLayout.addWidget(self.linkCardView)
        linkCardLayout.setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.setMinimumHeight(350)
        self.setMaximumHeight(self.banner.height())

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 20, 0, 0)
        self.vBoxLayout.addWidget(self.galleryLabel)
        self.vBoxLayout.addLayout(linkCardLayout)
        self.vBoxLayout.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )

        self.linkCardView.addCard(
            FluentIcon.GITHUB,
            self.tr("GitHub repo"),
            self.tr(""),
            CoreArgs._core_link_github,
        )
        self._connectSignalToSlot()

    def _connectSignalToSlot(self) -> None:
        core_signalbus.configUpdated.connect(self._onConfigUpdated)

    def _onConfigUpdated(
        self,
        names: tuple[str, str],
        config_key: str,
        value_tuple: tuple[Any,],
        parent_keys: list[str],
    ) -> None:
        if names[0] == self.main_config.name:
            (value,) = value_tuple
            if config_key == "appBackground":
                self.show_banner = not bool(value)
                self.is_background_active = bool(value)
            elif config_key == "backgroundOpacity":
                self.show_banner = not self.is_background_active or int(value) == 0

    def paintEvent(self, e):
        super().paintEvent(e)
        if self.show_banner and not self.banner.isNull():
            painter = QPainter(self)
            painter.setRenderHints(
                QPainter.RenderHint.SmoothPixmapTransform
                | QPainter.RenderHint.Antialiasing
            )
            painter.setPen(Qt.PenStyle.NoPen)

            path = QPainterPath()
            path.setFillRule(Qt.FillRule.WindingFill)
            w, h = self.width(), 200
            path.addRoundedRect(QRectF(0, 0, w, h), 10, 10)
            path.addRect(QRectF(0, h - 50, 50, 50))
            path.addRect(QRectF(w - 50, 0, 50, 50))
            path.addRect(QRectF(w - 50, h - 50, 50, 50))
            path = path.simplified()

            # Calculate the required height for maintaining image aspect ratio
            image_height = self.width() * self.banner.height() // self.banner.width()

            # draw banner image with aspect ratio preservation
            pixmap = self.banner.scaled(
                self.width(),
                image_height,
                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                transformMode=Qt.TransformationMode.SmoothTransformation,
            )
            path.addRect(QRectF(0, h, w, self.height() - h))
            painter.fillPath(path, QBrush(pixmap))


class CoreHomeInterface(ScrollArea):
    def __init__(self, main_config: AnyConfig, parent: Optional[QWidget] = None):
        super().__init__(parent=parent)
        self._view = QWidget(self)
        self.banner = BannerWidget(
            main_config=main_config, banner_path=CoreArgs._core_banner_path, parent=self
        )
        self.vBoxLayout = QVBoxLayout(self._view)
        self._initWidget()

    def _initWidget(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidget(self._view)
        self.setWidgetResizable(True)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 36)
        self.vBoxLayout.setSpacing(40)
        self.vBoxLayout.addWidget(self.banner, stretch=2)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._setQss()

    def _setQss(self):
        self._view.setObjectName("view")
        self.setObjectName("homeInterface")
        CoreStyleSheet.HOME_INTERFACE.apply(self)
