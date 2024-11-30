from copy import deepcopy
from typing import Any, Optional
from qfluentwidgets import (
    ScrollArea,
    PrimaryPushButton,
    PushButton,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

import traceback

from ...common.core_stylesheet import CoreStyleSheet
from ...common.core_signalbus import core_signalbus
from ...components.console_view import ConsoleView
from ...components.flow_area import FlowArea
from ...components.infobar_test import InfoBar, InfoBarPosition
from .process_subinterface import ProcessSubinterface

from ....module.concurrency.process.process_generator import ProcessGenerator
from ....module.concurrency.thread.thread_ui_streamer import ThreadUIStreamer
from ....module.config.app_config import AppConfig
from ....module.config.internal.app_args import AppArgs
from ....module.config.templates.template_enums import UIFlags
from ....module.config.templates.app_template import AppTemplate
from ....module.config.app_config import AppConfig
from ....module.logging import logger


class CoreProcessInterface(ScrollArea):
    _logger = logger
    _app_config = AppConfig()

    def __init__(
        self,
        ProcessGenerator: ProcessGenerator,
        ThreadManager: ThreadUIStreamer,
        parent: Optional[QWidget] = None,
    ) -> None:
        try:
            super().__init__(parent)
            self._view = QWidget(self)
            self.titleLabel = QLabel(self.tr(f"{AppArgs.app_name} Process Manager"))
            self.terminateAllButton = PushButton(self.tr("Terminate All"))
            self.startButton = PrimaryPushButton(self.tr("Start All"))
            self.flowConsoles = FlowArea()
            self.processSubinterface = ProcessSubinterface(
                config=self._app_config, template=self._createProcessTemplate()
            )

            self.vGeneralLayout = QVBoxLayout(self._view)
            self.hButtonLayout = QHBoxLayout()
            self.hMainLayout = QHBoxLayout()

            self.max_threads = self._app_config.getValue("maxThreads")
            self.terminal_size = self._app_config.getValue("terminalSize")
            self.console_widgets = {}  # type: dict[int, ConsoleView | None]

            self.threadManager = ThreadManager(self.max_threads, self.console_widgets)
            self.process_generator = ProcessGenerator()
            self.process_running = False

            self._initWidget()
            self._initLayout()
            self._initConsole()
            self._connectSignalToSlot()
            core_signalbus.isProcessesRunning.emit(False)  # Set inital state
        except Exception:
            self.deleteLater()
            raise

    def _createProcessTemplate(self) -> AppTemplate:
        # REVIEW: Consider creating new template class for use here instead of pulling stuff out from app template
        app_template = AppTemplate()
        template_topkey = "Process"
        template_options = deepcopy(app_template.getValue(template_topkey))

        template_dict = {template_topkey: {}}
        for k, v in template_options.items():
            if "ui_flags" in v and UIFlags.EXCLUDE in v["ui_flags"]:
                v.pop("ui_flags")
                template_dict[template_topkey] |= {k: v}

        template = AppTemplate.createSubTemplate(
            template_name="Process",
            template=template_dict,
            icons=app_template.getIcons(),
        )
        return template

    def _initWidget(self) -> None:
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 0)
        self.setWidget(self._view)
        self.setWidgetResizable(True)
        self._setQss()

    def _setQss(self) -> None:
        self.setObjectName("processInterface")
        self._view.setObjectName("view")
        self.titleLabel.setObjectName("Label")
        CoreStyleSheet.PROCESS_INTERFACE.apply(self)

    def _initLayout(self) -> None:
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

    def _addConsoles(self, amount: int) -> None:
        ids = []
        start = len(self.console_widgets)
        sizeHint = QSize(self.terminal_size, self.terminal_size)
        if start:
            # Re-add previously removed consoles
            for i, console in self.console_widgets.items():
                if console is None and amount > 0:
                    amount -= 1
                    console = ConsoleView(
                        process_id=i, sizeHint=sizeHint, parent=self._view
                    )
                    self.console_widgets[i] = console
                    self.flowConsoles.flowLayout.addWidget(console)
                    ids.append(i)

        stop = start + amount
        # Add *amount* new consoles (minus those re-added)
        for i in range(start, stop):
            console = ConsoleView(process_id=i, sizeHint=sizeHint, parent=self._view)
            self.console_widgets |= {i: console}
            self.flowConsoles.flowLayout.addWidget(console)
            ids.append(i)
        self.threadManager.consoleCountChanged.emit(ids)

    def _removeConsoles(self, amount: int, indices: Optional[list[int]] = None) -> None:
        iterator = indices if indices else reversed(self.console_widgets)
        for i in iterator:
            console = self.console_widgets[i]
            if console and amount:
                amount -= 1
                self.flowConsoles.flowLayout.removeWidget(console)
                console.deleteLater()
                self.console_widgets[i] = None
        self.flowConsoles.flowLayout.update()

    def _initConsole(self, allowRemoval: bool = True) -> None:
        if self.console_widgets:
            availableConsoles = len(
                [console for console in self.console_widgets.values() if console]
            )
            if availableConsoles < self.max_threads:
                self._addConsoles(self.max_threads - availableConsoles)
            elif allowRemoval and availableConsoles > self.max_threads:
                self._removeConsoles(availableConsoles - self.max_threads)
        else:
            self._addConsoles(self.max_threads)

    def _connectSignalToSlot(self) -> None:
        core_signalbus.configUpdated.connect(self._onConfigUpdated)
        core_signalbus.isProcessesRunning.connect(self._onProcessRunning)

        self.terminateAllButton.clicked.connect(self._onTerminateAllButtonClicked)
        self.startButton.clicked.connect(self._onStartButtonClicked)

        self.threadManager.currentProgress.connect(
            self.processSubinterface.getProgressCard().progressWidget.setValue
        )
        self.threadManager.totalProgress.connect(
            lambda max: self.processSubinterface.getProgressCard().progressWidget.setRange(
                0, max
            )
        )
        self.threadManager.threadsRemoved.connect(
            lambda threadIDs: self._removeConsoles(len(threadIDs), threadIDs)
        )
        self.threadManager.finished.connect(self._onThreadManagerFinished)
        self.threadManager.consoleTextStream.connect(self._onConsoleTextReceived)
        self.threadManager.clearConsole.connect(self._onClearConsole)

    def _onConfigUpdated(
        self, config_name: str, configkey: str, value_tuple: tuple[Any,]
    ) -> None:
        if config_name == self._app_config.getConfigName():
            (value,) = value_tuple
            if configkey == "maxThreads":
                self.max_threads = value
                self._initConsole(allowRemoval=not self.process_running)
                self.threadManager.updateMaxThreads.emit(self.max_threads)
            elif configkey == "terminalSize":
                self.terminal_size = value
                for console in self.console_widgets.values():
                    if console:
                        console.updateSizeHint(QSize(value, value))

    def _onProcessRunning(self, is_running: bool) -> None:
        self.terminateAllButton.setEnabled(is_running)
        self.process_running = is_running

    def _onTerminateAllButtonClicked(self) -> None:
        self.threadManager.kill.emit(False)  # Include self: True/False
        core_signalbus.isProcessesRunning.emit(False)
        self.processSubinterface.getProgressCard().stop()

    def _onMissingInput(self) -> None:
        InfoBar.warning(
            title=self.tr("No input!"),
            content=self.tr("Please enter input before proceeding"),
            isClosable=False,
            duration=5000,
            position=InfoBarPosition.TOP,
            parent=self,
        )

    def _onStartButtonClicked(self) -> None:
        try:
            if self.process_generator.canStart():
                self.processSubinterface.getProgressCard().start()
                self.threadManager.setProcessGenerator(self.process_generator)
                self.threadManager.start()
                core_signalbus.isProcessesRunning.emit(True)
            else:
                self._onMissingInput()
        except Exception:
            self._logger.error(
                f"Process Manager failed\n"
                + traceback.format_exc(limit=AppArgs.traceback_limit)
            )

    def _onThreadManagerFinished(self) -> None:
        core_signalbus.isProcessesRunning.emit(False)

    def _onConsoleTextReceived(self, process_id: int, text: str) -> None:
        self.console_widgets[process_id].append(text)

    def _onClearConsole(self, process_id: int) -> None:
        self.console_widgets[process_id].clear()
