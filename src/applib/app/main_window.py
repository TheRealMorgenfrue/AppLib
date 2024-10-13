from contextlib import redirect_stdout
import traceback
from typing import Any

with redirect_stdout(None):
    from qfluentwidgets import (
        NavigationItemPosition,
        MSFluentWindow,
        SplashScreen,
        NavigationBarPushButton,
        toggleTheme,
        setTheme,
        theme,
        setThemeColor,
        Theme,
    )
    from qfluentwidgets import FluentIcon as FIF

from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPaintEvent
from PyQt6.QtWidgets import (
    QApplication,
    QGraphicsBlurEffect,
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
)
from PyQt6.QtCore import QSize, Qt

from .common.core_signalbus import core_signalbus
from .common.core_stylesheet import CoreStyleSheet
from .components.infobar_test import InfoBar, InfoBarPosition

from module.config.internal.app_args import AppArgs
from module.config.internal.testargs import TestArgs
from module.config.internal.names import ModuleNames
from module.logging import logger


class MainWindow(MSFluentWindow):
    _logger = logger

    def __init__(self):
        super().__init__()
        self.background = None  # type: QPixmap | None
        self.backgroundOpacity = 0.0
        self.backgroundBlurRadius = 0.0
        self.errorLog = []
        self.logmsg = f"Please check the log for details"
        self.setMicaEffectEnabled(False)
        setTheme(Theme.AUTO, lazy=True)

        try:
            self.__initWindow()

            from module.config.app_config import AppConfig

            self._app_config = AppConfig()

            self.__connectSignalToSlot()

            # The rest of the modules imported here to make sure
            # the splash screen is loaded before anything else
            try:
                from .settings_interface import SettingsInterface

                self.settingsInterface = SettingsInterface(self)
            except Exception:
                self.errorLog.append(
                    traceback.format_exc(limit=TestArgs.traceback_limit)
                )
                self.settingsInterface = None

            try:
                from .home_interface import HomeInterface

                self.homeInterface = HomeInterface(self)
            except Exception:
                self.errorLog.append(
                    traceback.format_exc(limit=TestArgs.traceback_limit)
                )
                self.homeInterface = None

            try:
                from .process_interface import ProcessInterface

                self.processInterface = ProcessInterface(self)
            except Exception:
                self.errorLog.append(
                    traceback.format_exc(limit=TestArgs.traceback_limit)
                )
                self.processInterface = None

            self.__initNavigation()
            self._initBackground()
        except Exception:
            self.errorLog.append(traceback.format_exc(limit=TestArgs.traceback_limit))

        CoreStyleSheet.MAIN_WINDOW.apply(self)
        self.splashScreen.finish()

        if self.errorLog:
            self._displayErrors()
            self._logger.warning("Application started with errors")
        else:
            self._logger.info("Application startup successful!")
            self._checkSoftErrors()

    def _initBackground(self):
        val = self._app_config.getValue("appBackground")
        self.background = QPixmap(val) if val else None  # type: QPixmap | None
        self.backgroundOpacity = (
            self._app_config.getValue("backgroundOpacity", 0.0) / 100
        )
        self.backgroundBlurRadius = float(
            self._app_config.getValue("backgroundBlur", 0.0)
        )

    def __initNavigation(self):
        if self.homeInterface:
            self.addSubInterface(self.homeInterface, FIF.HOME, self.tr("Home"))
        if self.processInterface:
            self.addSubInterface(self.processInterface, FIF.IOT, self.tr("Process"))

        self.navigationInterface.addWidget(
            "themeButton",
            NavigationBarPushButton(FIF.CONSTRACT, "", isSelectable=False),
            self.toggleTheme,
            NavigationItemPosition.BOTTOM,
        )

        if self.settingsInterface:
            self.addSubInterface(
                self.settingsInterface,
                FIF.SETTING,
                self.tr("Settings"),
                position=NavigationItemPosition.BOTTOM,
            )

    def __initWindow(self):
        # self.titleBar.maxBtn.setHidden(True)
        # self.titleBar.maxBtn.setDisabled(True)
        # self.titleBar.setDoubleClickEnabled(False)
        # self.setResizeEnabled(False)
        self.setMinimumSize(960, 700)
        self.resize(1280, 720)
        # REVIEW: Set your own icon!
        self.setWindowIcon(QIcon(f"{AppArgs.logo_dir}/logo.png"))
        self.setWindowTitle(f"{ModuleNames.app_name} {TestArgs.app_version}")

        # Create splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(128, 128))
        self.splashScreen.raise_()

        # Calculate window position
        desktop = QApplication.primaryScreen().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        # Setup rendering for background image
        self.scene = QGraphicsScene()
        self.view = QGraphicsView()

        self.show()
        QApplication.processEvents()

    def __connectSignalToSlot(self) -> None:
        core_signalbus.configUpdated.connect(self.__onConfigUpdated)
        core_signalbus.configValidationError.connect(
            lambda configname, title, content: self.__onConfigValidationFailed(
                title, content
            )
        )
        core_signalbus.configStateChange.connect(self.__onConfigStateChange)
        core_signalbus.genericError.connect(self.__onGenericError)

    def __onConfigUpdated(
        self, config_name: str, configkey: str, valuePack: tuple[Any,]
    ) -> None:
        if config_name == self._app_config.getConfigName():
            (value,) = valuePack
            if configkey == "appBackground":
                self.background = QPixmap(value) if value else None
                self.update()
            elif configkey == "appTheme":
                self.__onThemeChanged(value)
            elif configkey == "appColor":
                setThemeColor(value, lazy=True)
            elif configkey == "backgroundOpacity":
                self.backgroundOpacity = value / 100
                self.update()
            elif configkey == "backgroundBlur":
                self.backgroundBlurRadius = float(value)
                self.update()

    def __onThemeChanged(self, value: str):
        if value == "Light":
            setTheme(Theme.LIGHT, lazy=True)
        elif value == "Dark":
            setTheme(Theme.DARK, lazy=True)
        else:
            setTheme(Theme.AUTO, lazy=True)

    def __onGenericError(self, title: str, content: str) -> None:
        InfoBar.error(
            title=self.tr(title),
            content=(self.tr(content) if content else self.logmsg),
            orient=(Qt.Orientation.Vertical if content else Qt.Orientation.Horizontal),
            isClosable=True,
            duration=7000,
            position=InfoBarPosition.TOP,
            parent=self,
        )

    def __onConfigValidationFailed(self, title: str, content: str) -> None:
        if not title:
            title = "Invalid value (no information given)"  # Placeholder message when no message is given
            InfoBar.warning(
                title=self.tr(title),
                content=self.tr(content),
                orient=(
                    Qt.Orientation.Vertical if content else Qt.Orientation.Horizontal
                ),
                isClosable=False,
                duration=5000,
                position=InfoBarPosition.TOP,
                parent=self,
            )

    def __onConfigStateChange(self, state: bool, title: str, content: str) -> None:
        if state:
            InfoBar.success(
                title=self.tr(title),
                content=self.tr(content),
                orient=(
                    Qt.Orientation.Vertical if content else Qt.Orientation.Horizontal
                ),
                isClosable=False,
                duration=5000,
                position=InfoBarPosition.TOP,
                parent=self,
            )
        else:
            InfoBar.error(
                title=self.tr(title),
                content=self.tr(content) if content else self.logmsg,
                orient=(
                    Qt.Orientation.Vertical if content else Qt.Orientation.Horizontal
                ),
                isClosable=False,
                duration=5000,
                position=InfoBarPosition.TOP,
                parent=self,
            )

    def _checkSoftErrors(self) -> None:
        if self._app_config.getFailureStatus():
            InfoBar.warning(
                title=self.tr("Using internal config"),
                content=self.tr("Setting changes may not persist"),
                orient=Qt.Orientation.Vertical,
                isClosable=True,
                duration=-1,
                position=InfoBarPosition.TOP,
                parent=self,
            )

    def _displayErrors(self) -> None:
        for error in self.errorLog:
            self._logger.critical(
                "Encountered a critical error during startup\n" + error
            )
            InfoBar.error(
                title=self.tr("Critical Error!"),
                content=error,
                isClosable=True,
                duration=-1,
                position=InfoBarPosition.TOP,
                parent=self,
            )

    def toggleTheme(self) -> None:
        toggleTheme(lazy=True)
        core_signalbus.updateConfigSettings.emit(
            self._app_config.getConfigName(), "appTheme", (theme().value,)
        )
        core_signalbus.doSaveConfig.emit(self._app_config.getConfigName())

    def paintEvent(self, e: QPaintEvent) -> None:
        super().paintEvent(e)
        if self.background:
            # Only set scene once!
            if not self.view.scene():
                self.view.setScene(self.scene)

            # Setup painter
            painter = QPainter(self)
            painter.setRenderHints(
                QPainter.RenderHint.SmoothPixmapTransform
                | QPainter.RenderHint.Antialiasing
                | QPainter.RenderHint.LosslessImageRendering
            )
            painter.setPen(Qt.PenStyle.NoPen)

            # Draw background image with aspect ratio preservation
            pixmap = self.background.scaled(
                self.width(),
                self.height(),
                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                transformMode=Qt.TransformationMode.SmoothTransformation,
            )

            # Get new pixmap rect
            rect = pixmap.rect().toRectF()

            # Add blur effect
            blur = QGraphicsBlurEffect()
            blur.setBlurRadius(self.backgroundBlurRadius)
            blur.setBlurHints(QGraphicsBlurEffect.BlurHint.QualityHint)

            # Create pixmap for the graphics scene
            pixmapItem = QGraphicsPixmapItem(pixmap)
            pixmapItem.setGraphicsEffect(blur)
            pixmapItem.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresParentOpacity)
            pixmapItem.setOpacity(self.backgroundOpacity)

            # Add image with effects to the scene and render image
            self.scene.clear()
            self.scene.addItem(pixmapItem)
            self.view.render(painter, rect, rect.toRect())
