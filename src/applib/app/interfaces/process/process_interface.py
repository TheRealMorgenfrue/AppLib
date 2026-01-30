import traceback
from typing import Any

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget
from qfluentwidgets import PrimaryPushButton, PushButton, ScrollArea

from ....module.concurrency.process.process_generator import ProcessGeneratorBase
from ....module.concurrency.thread.thread_manager import ThreadManager
from ....module.concurrency.thread.thread_manager_gui import ThreadManagerGui
from ....module.configuration.internal.core_args import CoreArgs
from ....module.logging import LoggingManager
from ....module.tools.types.config import AnyConfig
from ....module.tools.types.templates import AnyTemplate
from ...common.core_signalbus import core_signalbus
from ...common.core_stylesheet import CoreStyleSheet
from ...components.console_view import ConsoleView
from ...components.flow_area import FlowArea
from .process_subinterface import ProcessSubinterface


class CoreProcessInterface(ScrollArea):
    _process_msg_signal = pyqtSignal(str, int, str)
    """Send messages to the main thread (Process) from anywhere.\n
    level: str, pid: int, msg: str
    """

    def __init__(
        self,
        main_config: AnyConfig,
        process_template: AnyTemplate,
        ProcessGenerator: type[ProcessGeneratorBase],
        ThreadManager: type[ThreadManagerGui],
        parent: QWidget | None = None,
    ):
        try:
            super().__init__(parent)
            self._logger = LoggingManager()
            self.main_config = main_config
            self.max_threads = self.main_config.get_value("maxThreads")
            self.process_running = False
            self.terminal_size = self.main_config.get_value("terminalSize")
            self.console_widgets = {}  # type: dict[int, ConsoleView | None]

            self._view = QWidget(self)
            self.titleLabel = QLabel(
                self.tr(f"{CoreArgs._core_app_name} Process Manager")
            )
            self.terminateAllButton = PushButton(self.tr("Terminate All"))
            self.startButton = PrimaryPushButton(self.tr("Start All"))
            self.flowConsoles = FlowArea()
            self.processSubinterface = ProcessSubinterface(
                config=self.main_config, template=process_template
            )
            self.vGeneralLayout = QVBoxLayout(self._view)
            self.hButtonLayout = QHBoxLayout()
            self.hMainLayout = QHBoxLayout()

            self.thread_manager = ThreadManager(
                self.max_threads, ProcessGenerator, self.console_widgets
            )

            self._initWidget()
            self._initLayout()
            self._initConsole()
            self._setEnableTerminateButtons(False)
            self.__connectSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    def _initWidget(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 0)
        self.setWidget(self._view)
        self.setWidgetResizable(True)
        self._setQss()

    def _setQss(self):
        self.setObjectName("processInterface")
        self._view.setObjectName("view")
        self.titleLabel.setObjectName("Label")
        CoreStyleSheet.PROCESS_INTERFACE.apply(self)

    def _initLayout(self):
        self.terminateAllButton.setMaximumWidth(150)
        self.startButton.setMaximumWidth(150)

        self.hButtonLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.hButtonLayout.setSpacing(20)
        self.hButtonLayout.addWidget(self.terminateAllButton, 1)
        self.hButtonLayout.addWidget(self.startButton, 1)

        self.hMainLayout.setContentsMargins(0, 0, 0, 0)
        self.hMainLayout.setSpacing(20)
        self.hMainLayout.addWidget(self.flowConsoles, 3)
        self.hMainLayout.addWidget(self.processSubinterface, 1)

        self.vGeneralLayout.setContentsMargins(20, 0, 20, 0)
        self.vGeneralLayout.addWidget(self.titleLabel)
        self.vGeneralLayout.addLayout(self.hButtonLayout)
        self.vGeneralLayout.addSpacing(20)
        self.vGeneralLayout.addLayout(self.hMainLayout)

    def _addConsoles(self, amount: int):
        ids = []
        start = len(self.console_widgets)
        sizeHint = QSize(self.terminal_size, self.terminal_size)
        if start:
            # Re-add previously removed consoles
            for i, console in self.console_widgets.items():
                if console is None and amount > 0:
                    amount -= 1
                    console = ConsoleView(
                        process_id=i,
                        label=f"Process {i}",
                        sizeHint=sizeHint,
                        parent=self._view,
                    )
                    self.console_widgets[i] = console
                    self.flowConsoles.flowLayout.addWidget(console)
                    ids.append(i)

        stop = start + amount
        # Add *amount* new consoles (minus those re-added)
        for i in range(start, stop):
            console = ConsoleView(
                process_id=i, label=f"Process {i}", sizeHint=sizeHint, parent=self._view
            )
            self.console_widgets[i] = console
            self.flowConsoles.flowLayout.addWidget(console)
            ids.append(i)
        self.thread_manager.console_count_changed.emit(ids)

    def _removeConsoles(self, amount: int, indices: list[int] | None = None):
        iterator = indices if indices else reversed(self.console_widgets)
        for i in iterator:
            console = self.console_widgets[i]
            if console and amount:
                amount -= 1
                self.flowConsoles.flowLayout.removeWidget(console)
                console.deleteLater()
                self.console_widgets[i] = None
        self.flowConsoles.flowLayout.update()

    def _initConsole(self, allow_removal: bool = True):
        if self.console_widgets:
            availableConsoles = len(
                [console for console in self.console_widgets.values() if console]
            )
            if availableConsoles < self.max_threads:
                self._addConsoles(self.max_threads - availableConsoles)
            elif allow_removal and availableConsoles > self.max_threads:
                self._removeConsoles(availableConsoles - self.max_threads)
        else:
            self._addConsoles(self.max_threads)

    def __connectSignalToSlot(self) -> None:
        core_signalbus.configUpdated.connect(self._onConfigUpdated)
        self._process_msg_signal.connect(self._onProcessMsgReceived)
        self.terminateAllButton.clicked.connect(self.thread_manager.terminate_all.emit)
        self.startButton.clicked.connect(self._onStartButtonClicked)

        self.thread_manager.current_progress.connect(
            self.processSubinterface.getProgressCard().progressWidget.setValue
        )
        self.thread_manager.total_progress.connect(
            lambda max: self.processSubinterface.getProgressCard().progressWidget.setRange(
                0, max
            )
        )
        self.thread_manager.thread_removed.connect(self._onThreadRemoved)
        self.thread_manager.clear_console.connect(self._onClearConsole)
        self.thread_manager.change_state.connect(self._onThreadManagerStateChange)

    def _onConfigUpdated(
        self,
        names: tuple[str, str],
        config_key: str,
        value_tuple: tuple[Any,],
        path: str,
    ) -> None:
        if names[0] == self.main_config.name:
            (value,) = value_tuple
            if config_key == "maxThreads":
                self.max_threads = value
                self._initConsole(allow_removal=not self.process_running)
                self.thread_manager.max_threads = self.max_threads
            elif config_key == "terminalSize":
                self.terminal_size = value
                for console in self.console_widgets.values():
                    if console:
                        console.updateSizeHint(QSize(value, value))

    def _onThreadRemoved(self, thread_id: int):
        count = 0
        for console in self.console_widgets.values():
            if console:
                count += 1
        if count > self.max_threads:
            self._removeConsoles(1, [thread_id])

    def _onThreadManagerStateChange(self, state: ThreadManager.State):
        process_running = False
        match state:
            case ThreadManager.State.Stopped:
                self.processSubinterface.getProgressCard().stop()
                self.startButton.setDisabled(False)
            case ThreadManager.State.Running:
                self._logger.set_process_signal(self._process_msg_signal)
                self.startButton.setDisabled(True)
                process_running = True
        self.process_running = process_running

        self._setEnableTerminateButtons(self.process_running)

    def _onStartButtonClicked(self):
        try:
            self.processSubinterface.getProgressCard().start()
            self.thread_manager.start()
        except Exception:
            self._logger.set_process_signal(None)
            self._logger.error(
                f"Process Manager failed\n"
                + traceback.format_exc(limit=CoreArgs._core_traceback_limit),
                gui=True,
            )

    def _setEnableTerminateButtons(self, value: bool):
        if self.terminateAllButton.isEnabled() == value:
            return

        self.terminateAllButton.setEnabled(value)
        for console in self.console_widgets.values():
            if console:
                console.terminateButton.setEnabled(value)

    def _onProcessMsgReceived(self, level: str, pid: int, msg: str):
        match level.lower():
            case "debug":
                self._debug(pid, msg)
            case "info":
                self._info(pid, msg)
            case "warning":
                self._warning(pid, msg)
            case "error":
                self._error(pid, msg)
            case "critical":
                self._critical(pid, msg)

    def _debug(self, process_id: int, text: str):
        console = self.console_widgets[process_id]
        if console:
            color = QColor("#2abdc7")  # if isDarkTheme() else QColor("#2abdc7")
            console.append(text, color=color)

    def _info(self, process_id: int, text: str):
        console = self.console_widgets[process_id]
        if console:
            color = QColor("white")  # if isDarkTheme() else QColor("black")
            console.append(text, color=color)

    def _warning(self, process_id: int, text: str):
        console = self.console_widgets[process_id]
        if console:
            color = QColor("#ffe228")  # if isDarkTheme() else QColor("#a9941b")
            console.append(text, color=color, bold=True)

    def _error(self, process_id: int, text: str):
        console = self.console_widgets[process_id]
        if console:
            color = QColor("#ff0000")  # if isDarkTheme() else QColor("#9e0000")
            console.append(text, color=color, bold=True)

    def _critical(self, process_id: int, text: str):
        console = self.console_widgets[process_id]
        if console:
            color = QColor("#ff0000")  # if isDarkTheme() else QColor("#9e0000")
            console.append(text, color=color, bold=True)

    def _onClearConsole(self, process_id: int):
        console = self.console_widgets[process_id]
        if console:
            console.clear()
