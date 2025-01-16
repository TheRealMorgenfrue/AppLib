import traceback
from typing import Any, Optional, Union

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
    FluentIconBase,
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
    QWidget,
)
from PyQt6.QtCore import QSize, Qt

from ..common.core_signalbus import core_signalbus
from ..common.core_stylesheet import CoreStyleSheet
from ..components.infobar_test import InfoBar, InfoBarPosition
from ...module.config.internal.core_args import CoreArgs
from ...module.config.core_config import CoreConfig
from ...module.logging import AppLibLogger
from ...module.tools.decorators import makeSetupArgs
from ...module.tools.types.config import AnyConfig


class CoreMainWindow(MSFluentWindow):
    def __init__(
        self,
        MainArgs,
        MainConfig: Optional[AnyConfig] = None,
        subinterfaces: Optional[
            list[tuple[QWidget, Union[str, QIcon, FluentIconBase], str]]
        ] = None,
        settings_interface: Optional[
            tuple[QWidget, Union[str, QIcon, FluentIconBase], str]
        ] = None,
    ):
        # Copy MainArgs attributes to CoreArgs, overriding its attributes if possible
        makeSetupArgs(MainArgs)

        # Initialize logger after MainArgs is read
        applogger = AppLibLogger()
        applogger.setLogDir(CoreArgs._core_log_dir)
        applogger.writeHeaderToLog()
        self._logger = applogger.getLogger()

        super().__init__()
        self._subinterfaces = subinterfaces
        self._settings_tuple = settings_interface
        self._error_log = []
        self._default_logmsg = f"Please check the log for details"
        self.background = None  # type: QPixmap | None
        self.background_opacity = 0.0
        self.background_blur_radius = 0.0

        self.setMicaEffectEnabled(False)
        setTheme(Theme.AUTO, lazy=True)
        self._initWindow()

        try:
            # Initialize the main config
            self.main_config = CoreConfig() if MainConfig is None else MainConfig()

            self._connectSignalToSlot()
            self._initNavigation()
            self._initBackgroundAndTheme()
            self._checkSoftErrors()
        except Exception:
            self._error_log.append(
                traceback.format_exc(limit=CoreArgs._core_traceback_limit)
            )

        CoreStyleSheet.MAIN_WINDOW.apply(self)
        self.splashScreen.finish()
        self._displayErrors()

    def _initBackgroundAndTheme(self):
        val = self.main_config.getValue("appBackground")
        self.background = QPixmap(val) if val else None  # type: QPixmap | None
        self.background_opacity = (
            self.main_config.getValue("backgroundOpacity", 0.0) / 100
        )
        self.background_blur_radius = float(
            self.main_config.getValue("backgroundBlur", 0.0)
        )
        self._onThemeChanged(self.main_config.getValue("appTheme"))

    def _initNavigation(self):
        if self._subinterfaces:
            created_interfaces = []
            for Interface, icon, title in self._subinterfaces:
                try:
                    init_interface = Interface(parent=self)
                    self.addSubInterface(
                        interface=init_interface, icon=icon, text=self.tr(title)
                    )
                    created_interfaces.append(init_interface)
                except Exception:
                    self._error_log.append(
                        traceback.format_exc(limit=CoreArgs._core_traceback_limit)
                    )
            self._subinterfaces = created_interfaces

        self.navigationInterface.addWidget(
            "themeButton",
            NavigationBarPushButton(FIF.CONSTRACT, "", isSelectable=False),
            self.toggleTheme,
            NavigationItemPosition.BOTTOM,
        )

        if self._settings_tuple:
            Interface, icon, title = self._settings_tuple
            self.addSubInterface(
                interface=Interface(parent=self),
                icon=icon,
                text=self.tr(title),
                position=NavigationItemPosition.BOTTOM,
            )

    def _initWindow(self):
        # self.titleBar.maxBtn.setHidden(True)
        # self.titleBar.maxBtn.setDisabled(True)
        # self.titleBar.setDoubleClickEnabled(False)
        # self.setResizeEnabled(False)
        self.setMinimumSize(960, 700)
        self.resize(1280, 720)
        self.setWindowIcon(
            QIcon(CoreArgs._core_main_logo_path)
            if isinstance(CoreArgs._core_main_logo_path, str)
            else CoreArgs._core_main_logo_path
        )
        self.setWindowTitle(f"{CoreArgs._core_app_name} {CoreArgs._core_app_version}")

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
        self._view = QGraphicsView()

        self.show()
        QApplication.processEvents()

    def _connectSignalToSlot(self) -> None:
        core_signalbus.configUpdated.connect(self._onConfigUpdated)
        core_signalbus.configValidationError.connect(self._onConfigValidationFailed)
        core_signalbus.configStateChange.connect(self._onConfigStateChange)
        core_signalbus.genericError.connect(self._onGenericError)

    def _onConfigUpdated(
        self,
        config_name: str,
        config_key: str,
        parent_key: tuple[str | None],
        value_tuple: tuple[Any,],
    ) -> None:
        if config_name == self.main_config.getConfigName():
            (value,) = value_tuple
            if config_key == "appBackground":
                self.background = QPixmap(value) if value else None
                self.update()
            elif config_key == "appTheme":
                self._onThemeChanged(value)
            elif config_key == "appColor":
                setThemeColor(value, lazy=True)
            elif config_key == "backgroundOpacity":
                self.background_opacity = value / 100
                self.update()
            elif config_key == "backgroundBlur":
                self.background_blur_radius = float(value)
                self.update()

    def _onThemeChanged(self, value: str):
        if value == "Light":
            setTheme(Theme.LIGHT, lazy=True)
        elif value == "Dark":
            setTheme(Theme.DARK, lazy=True)
        else:
            setTheme(Theme.AUTO, lazy=True)

    def _onGenericError(self, title: str, content: str) -> None:
        InfoBar.error(
            title=self.tr(title),
            content=(self.tr(content) if content else self._default_logmsg),
            orient=(Qt.Orientation.Vertical if content else Qt.Orientation.Horizontal),
            isClosable=True,
            duration=7000,
            position=InfoBarPosition.TOP,
            parent=self,
        )

    def _onConfigValidationFailed(
        self, config_name: str, title: str, content: str
    ) -> None:
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

    def _onConfigStateChange(self, state: bool, title: str, content: str) -> None:
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
                content=self.tr(content) if content else self._default_logmsg,
                orient=(
                    Qt.Orientation.Vertical if content else Qt.Orientation.Horizontal
                ),
                isClosable=False,
                duration=5000,
                position=InfoBarPosition.TOP,
                parent=self,
            )

    def _checkSoftErrors(self) -> None:
        if self.main_config.getFailureStatus():
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
        for error in self._error_log:
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
            self.main_config.getConfigName(),
            "appTheme",
            (None,),
            (theme().value,),
        )
        core_signalbus.doSaveConfig.emit(self.main_config.getConfigName())

    def paintEvent(self, e: QPaintEvent) -> None:
        super().paintEvent(e)
        if self.background:
            # Only set scene once!
            if not self._view.scene():
                self._view.setScene(self.scene)

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
            blur.setBlurRadius(self.background_blur_radius)
            blur.setBlurHints(QGraphicsBlurEffect.BlurHint.QualityHint)

            # Create pixmap for the graphics scene
            pixmapItem = QGraphicsPixmapItem(pixmap)
            pixmapItem.setGraphicsEffect(blur)
            pixmapItem.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresParentOpacity)
            pixmapItem.setOpacity(self.background_opacity)

            # Add image with effects to the scene and render image
            self.scene.clear()
            self.scene.addItem(pixmapItem)
            self._view.render(painter, rect, rect.toRect())
