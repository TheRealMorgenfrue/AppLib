import os
import traceback
from typing import Any

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QPainter, QPaintEvent, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QGraphicsBlurEffect,
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QWidget,
)
from qfluentwidgets import (
    FluentIcon,
    FluentIconBase,
    MSFluentWindow,
    NavigationBarPushButton,
    NavigationItemPosition,
    SplashScreen,
    Theme,
    isDarkTheme,
    setTheme,
)

from applib.app.interfaces.process.process_interface import CoreProcessInterface
from applib.module.logging import LoggingManager
from applib.module.logging.logger_utils import create_main_logger, write_header_to_log

from ...module.configuration.config.core_config import CoreConfig
from ...module.configuration.internal.core_args import CoreArgs
from ...module.configuration.runners.actions.theme_actions import (
    change_theme,
    change_theme_color,
)
from ...module.tools.decorators import make_setup_args
from ...module.tools.types.config import AnyConfig
from ..common.core_signalbus import core_signalbus
from ..common.core_stylesheet import CoreStyleSheet
from ..components.infobar import InfoBar, InfoBarPosition


class CoreMainWindow(MSFluentWindow):
    gui_msg_signal = pyqtSignal(str, str, str, Qt.Orientation)
    """Send messages to the main thread (GUI) from anywhere.\n
    level: str, title: str, content: str, orient: Qt.Orientation
    """

    def __init__(
        self,
        MainArgs,
        MainConfig: type[AnyConfig] | None = None,
        subinterfaces: (
            list[tuple[type[QWidget], str | QIcon | FluentIconBase, str]] | None
        ) = None,
        settings_interface: (
            tuple[type[QWidget], str | QIcon | FluentIconBase, str] | None
        ) = None,
    ):
        # Copy MainArgs attributes to CoreArgs, overriding its attributes if possible
        make_setup_args(MainArgs)

        # Initialize logger after MainArgs is read
        self._logger = LoggingManager()
        create_main_logger()
        write_header_to_log()

        super().__init__()
        self._subinterfaces = subinterfaces
        self._settings_tuple = settings_interface
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
            self._check_soft_errors()
        except Exception:
            self._log_error(traceback.format_exc(limit=CoreArgs._core_traceback_limit))
        CoreStyleSheet.MAIN_WINDOW.apply(self)
        self.splashScreen.finish()
        self._connect_gui_logging()

    def _validate_background(self, image_path):
        return image_path and os.path.isfile(image_path)

    def _initBackgroundAndTheme(self):
        image_path = self.main_config.get_value("appBackground")
        self.background = (
            QPixmap(image_path) if self._validate_background(image_path) else None
        )  # type: QPixmap | None
        self.background_opacity = (
            self.main_config.get_value("backgroundOpacity", default=0.0) / 100
        )
        self.background_blur_radius = float(
            self.main_config.get_value("backgroundBlur", default=0.0)
        )
        change_theme(self.main_config.get_value("appTheme"))
        change_theme_color(self.main_config.get_value("appColor"))

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
                    if isinstance(init_interface, CoreProcessInterface):
                        self._logger.set_process_signal(
                            init_interface._process_msg_signal
                        )
                except Exception:
                    self._log_error(
                        traceback.format_exc(limit=CoreArgs._core_traceback_limit)
                    )
            self._subinterfaces = created_interfaces

        self.navigationInterface.addWidget(
            "themeButton",
            NavigationBarPushButton(FluentIcon.CONSTRACT, "", isSelectable=False),
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

    def _connectSignalToSlot(self):
        core_signalbus.configUpdated.connect(self._on_config_updated)

    def _connect_gui_logging(self):
        self.gui_msg_signal.connect(self._on_gui_msg_received)
        self._logger.set_gui_signal(self.gui_msg_signal)

    def _on_config_updated(
        self,
        names: tuple[str, str],
        config_key: str,
        value_tuple: tuple[Any,],
        path: str,
    ):
        if names[0] == self.main_config.name:
            (value,) = value_tuple
            if config_key == "appBackground":
                self.background = (
                    QPixmap(value) if self._validate_background(value) else None
                )
                self.update()
            elif config_key == "backgroundOpacity":
                self.background_opacity = value / 100
                self.update()
            elif config_key == "backgroundBlur":
                self.background_blur_radius = float(value)
                self.update()

    def _check_soft_errors(self):
        if self.main_config.failure:
            self._logger.warning(
                "Setting changes may not persist",
                title="Using internal config",
                gui=True,
            )

    def _log_error(self, error):
        self._logger.critical(
            msg="Encountered a critical error during startup\n" + error, gui=True
        )

    def _on_gui_msg_received(
        self, level: str, title: str, content: str, orient: Qt.Orientation
    ):
        match level.lower():
            case "info":
                self._info(title, content, orient)
            case "debug":
                self._debug(title, content, orient)
            case "warning":
                self._warning(title, content, orient)
            case "error":
                self._error(title, content, orient)
            case "critical":
                self._critical(title, content, orient)

    def _info(self, title: str, content: str, orient: Qt.Orientation):
        InfoBar.info(
            title=title,
            content=content,
            orient=orient,
            isClosable=True,
            duration=8000,
            position=InfoBarPosition.TOP_RIGHT,
            parent=self,
        )

    def _debug(self, title: str, content: str, orient: Qt.Orientation):
        w = InfoBar.new(
            icon=FluentIcon.DEVELOPER_TOOLS,
            title=title,
            content=content,
            orient=orient,
            isClosable=True,
            duration=8000,
            position=InfoBarPosition.TOP_RIGHT,
            parent=self,
        )
        if w:
            w.setCustomBackgroundColor(QColor("1c7e83"), QColor("2abdc7"))

    def _warning(self, title: str, content: str, orient: Qt.Orientation):
        InfoBar.warning(
            title=title,
            content=content,
            orient=orient,
            isClosable=True,
            duration=10000,
            position=InfoBarPosition.TOP_LEFT,
            parent=self,
        )

    def _error(self, title: str, content: str, orient: Qt.Orientation):
        InfoBar.error(
            title=title,
            content=content,
            orient=orient,
            isClosable=True,
            duration=10000,
            position=InfoBarPosition.TOP,
            parent=self,
        )

    def _critical(self, title: str, content: str, orient: Qt.Orientation):
        InfoBar.error(
            title=title,
            content=content,
            orient=orient,
            isClosable=True,
            duration=-1,
            position=InfoBarPosition.TOP,
            parent=self,
        )

    def toggleTheme(self):
        theme = Theme.LIGHT if isDarkTheme() else Theme.DARK
        core_signalbus.updateConfigSettings.emit(
            self.main_config.name, "appTheme", (theme.value,), ""
        )
        self.main_config.save_config()

    def paintEvent(self, e: QPaintEvent):
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
