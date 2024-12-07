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

from ...module.config.core_config import CoreConfig
from ...module.config.internal.core_args import CoreArgs
from ...module.config.templates.core_template import CoreTemplate
from ...module.logging import logger
from ...module.tools.types.config import AnyConfig
from ...module.tools.types.templates import AnyTemplate


class CoreMainWindow(MSFluentWindow):
    _logger = logger

    def __init__(
        self,
        main_config: AnyConfig = None,
        main_template: AnyTemplate = None,
        subinterfaces: list[
            tuple[QWidget, Union[str, QIcon, FluentIconBase], str]
        ] = None,
        settings_interface: Optional[
            tuple[QWidget, Union[str, QIcon, FluentIconBase], str] | None
        ] = None,
        app_icon: Union[str, QIcon] = f"{CoreArgs.logo_dir}/logo.png",
    ):
        super().__init__()
        self._app_icon = app_icon
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
            if main_config is None:
                self.main_config = CoreConfig()
            else:
                self.main_config = main_config

            if main_template is None:
                self.main_template = CoreTemplate()
            else:
                self.main_template = main_template

            self._connectSignalToSlot()
            self._initNavigation()
            self._initBackground()
        except Exception:
            self._error_log.append(traceback.format_exc(limit=CoreArgs.traceback_limit))

        CoreStyleSheet.MAIN_WINDOW.apply(self)
        self.splashScreen.finish()

        if self._error_log:
            self._displayErrors()
            self._logger.warning("Application started with errors")
        else:
            self._logger.info("Application startup successful!")
            self._checkSoftErrors()

    def _initBackground(self):
        val = self.main_config.getValue("appBackground")
        self.background = QPixmap(val) if val else None  # type: QPixmap | None
        self.background_opacity = (
            self.main_config.getValue("backgroundOpacity", 0.0) / 100
        )
        self.background_blur_radius = float(
            self.main_config.getValue("backgroundBlur", 0.0)
        )

    def _initNavigation(self):
        if self._subinterfaces:
            for Interface, icon, title in self._subinterfaces:
                try:
                    init_interface = Interface(parent=self)
                    self.addSubInterface(
                        interface=init_interface, icon=icon, text=self.tr(title)
                    )
                except Exception:
                    self._error_log.append(
                        traceback.format_exc(limit=CoreArgs.traceback_limit)
                    )

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
            QIcon(self._app_icon) if isinstance(self._app_icon, str) else self._app_icon
        )
        self.setWindowTitle(f"{CoreArgs.app_name} {CoreArgs.app_version}")

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
        core_signalbus.configValidationError.connect(
            lambda configname, title, content: self._onConfigValidationFailed(
                title, content
            )
        )
        core_signalbus.configStateChange.connect(self._onConfigStateChange)
        core_signalbus.genericError.connect(self._onGenericError)

    def _onConfigUpdated(
        self, config_name: str, configkey: str, value_tuple: tuple[Any,]
    ) -> None:
        if config_name == self.main_config.getConfigName():
            (value,) = value_tuple
            if configkey == "appBackground":
                self.background = QPixmap(value) if value else None
                self.update()
            elif configkey == "appTheme":
                self._onThemeChanged(value)
            elif configkey == "appColor":
                setThemeColor(value, lazy=True)
            elif configkey == "backgroundOpacity":
                self.background_opacity = value / 100
                self.update()
            elif configkey == "backgroundBlur":
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

    def _onConfigValidationFailed(self, title: str, content: str) -> None:
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
            self.main_config.getConfigName(), "appTheme", (theme().value,)
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
