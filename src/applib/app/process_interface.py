from typing import Any, Optional
from qfluentwidgets import (
    ScrollArea,
    FlowLayout,
    PrimaryPushButton,
    PushButton,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

import traceback

from .common.core_stylesheet import CoreStyleSheet
from .common.core_signalbus import core_signalbus
from .components.console_view import ConsoleView
from .components.infobar_test import InfoBar, InfoBarPosition
from .components.progresscards.progress_ring_card import ProgressRingCard
from .generators.cardwidget_generator import CardWidgetGenerator

from module.concurrency.process.process_generator import ProcessGenerator
from module.config.templates.app_template import AppTemplate
from module.concurrency.thread.thread_ui_streamer import ThreadUIStreamer
from module.config.app_config import AppConfig
from module.config.internal.app_args import AppArgs
from module.logging import logger


class ProcessSettings(ScrollArea):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)

        self._initWidget()
        self._initLayout()

    def _initWidget(self) -> None:
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 0)
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self._setQss()

    def _setQss(self) -> None:
        self.setObjectName("processSettings")
        self.view.setObjectName("view")
        CoreStyleSheet.PROCESS_INTERFACE.apply(self)

    def _initLayout(self) -> None:
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)

        app_template = AppTemplate()
        template_topkey = "Process"
        template_keys = [
            "maxThreads",
            "terminalSize",
        ]  # TODO: Create new template class for use here instead of pulling stuff out from app template
        template = AppTemplate.createSubTemplate(
            template_name=app_template.getName(),
            template={
                template_topkey: {
                    key: app_template.getValue(key=key) for key in template_keys
                }
            },
            icons=app_template.getIcons(),
        )
        generator = CardWidgetGenerator(
            config=AppConfig(),
            template=template,
            is_tight=True,
            parent=self,
        )
        for card in generator.getCards():
            self.vBoxLayout.addWidget(card)


class ProcessStatus(ScrollArea):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.view = QWidget(self)
        self.progressRingCard = ProgressRingCard(self.tr("Process Status"))

        self.vBoxLayout = QVBoxLayout(self.view)

        self._initWidget()
        self._initLayout()

    def _initWidget(self) -> None:
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 0)
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self._setQss()

    def _setQss(self) -> None:
        self.setObjectName("processStatus")
        self.view.setObjectName("view")
        CoreStyleSheet.PROCESS_INTERFACE.apply(self)

    def _initLayout(self) -> None:
        self.vBoxLayout.setContentsMargins(0, 20, 0, 0)
        self.vBoxLayout.addWidget(
            self.progressRingCard,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter,
        )


class ProcessSubinterface(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.vBoxLayout = QVBoxLayout(self)

        self.processStatus = ProcessStatus()
        self.processSettings = ProcessSettings()

        self._initLayout()

    def _initLayout(self) -> None:
        # self.setMinimumWidth(400)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(10)
        self.vBoxLayout.addWidget(self.processStatus, 2)
        self.vBoxLayout.addWidget(self.processSettings, 3)

    def getProgressCard(self) -> ProgressRingCard:
        return self.processStatus.progressRingCard


class FlowingConsoles(ScrollArea):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.view = QWidget(self)
        self.flowLayout = FlowLayout(self.view, needAni=True)

        self._initWidget()
        self._initLayout()

    def _initWidget(self) -> None:
        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 0)
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self._setQss()

    def _setQss(self) -> None:
        self.setObjectName("flowConsoles")
        self.view.setObjectName("view")
        CoreStyleSheet.PROCESS_INTERFACE.apply(self)

    def _initLayout(self) -> None:
        self.flowLayout.setContentsMargins(0, 0, 0, 0)
        self.flowLayout.setHorizontalSpacing(30)
        self.flowLayout.setVerticalSpacing(30)


class CoreProcessInterface(ScrollArea):
    _logger = logger
    _app_config = AppConfig()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        try:
            super().__init__(parent)
            self.view = QWidget(self)
            self.titleLabel = QLabel(self.tr(f"{AppArgs.app_name} Process Manager"))
            self.terminateAllButton = PushButton(self.tr("Terminate All"))
            self.startButton = PrimaryPushButton(self.tr("Start All"))
            self.flowConsoles = FlowingConsoles()
            self.processSubinterface = ProcessSubinterface()

            self.vGeneralLayout = QVBoxLayout(self.view)
            self.hButtonLayout = QHBoxLayout()
            self.hMainLayout = QHBoxLayout()

            self.maxThreads = self._app_config.getValue("maxThreads")
            self.terminalSize = self._app_config.getValue("terminalSize")
            self.consoleWidgets = {}  # type: dict[int, ConsoleView | None]
            self.threadManager = ThreadUIStreamer(self.maxThreads, self.consoleWidgets)
            # REVIEW: Add your own process generator!
            self.processGen = None  # ProcessGenerator()
            self.processRunning = False

            self._initWidget()
            self._initLayout()
            self._initConsole()
            self._connectSignalToSlot()
            core_signalbus.isProcessesRunning.emit(False)  # Set inital state
        except Exception:
            self.deleteLater()
            raise

    def _initWidget(self) -> None:
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 0)
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self._setQss()

    def _setQss(self) -> None:
        self.setObjectName("processInterface")
        self.view.setObjectName("view")
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
        start = len(self.consoleWidgets)
        sizeHint = QSize(self.terminalSize, self.terminalSize)
        if start:
            # Re-add previously removed consoles
            for i, console in self.consoleWidgets.items():
                if console is None and amount > 0:
                    amount -= 1
                    console = ConsoleView(
                        processID=i, sizeHint=sizeHint, parent=self.view
                    )
                    self.consoleWidgets[i] = console
                    self.flowConsoles.flowLayout.addWidget(console)
                    ids.append(i)

        stop = start + amount
        # Add *amount* new consoles (minus those re-added)
        for i in range(start, stop):
            console = ConsoleView(processID=i, sizeHint=sizeHint, parent=self.view)
            self.consoleWidgets |= {i: console}
            self.flowConsoles.flowLayout.addWidget(console)
            ids.append(i)
        self.threadManager.consoleCountChanged.emit(ids)

    def _removeConsoles(self, amount: int, indices: Optional[list[int]] = None) -> None:
        iterator = indices if indices else reversed(self.consoleWidgets)
        for i in iterator:
            console = self.consoleWidgets[i]
            if console and amount:
                amount -= 1
                self.flowConsoles.flowLayout.removeWidget(console)
                console.deleteLater()
                self.consoleWidgets[i] = None
        self.flowConsoles.flowLayout.update()

    def _initConsole(self, allowRemoval: bool = True) -> None:
        if self.consoleWidgets:
            availableConsoles = len(
                [console for console in self.consoleWidgets.values() if console]
            )
            if availableConsoles < self.maxThreads:
                self._addConsoles(self.maxThreads - availableConsoles)
            elif allowRemoval and availableConsoles > self.maxThreads:
                self._removeConsoles(availableConsoles - self.maxThreads)
        else:
            self._addConsoles(self.maxThreads)

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
        self, config_name: str, configkey: str, valuePack: tuple[Any,]
    ) -> None:
        if config_name == self._app_config.getConfigName():
            (value,) = valuePack
            if configkey == "maxThreads":
                self.maxThreads = value
                self._initConsole(allowRemoval=not self.processRunning)
                self.threadManager.updateMaxThreads.emit(self.maxThreads)
            elif configkey == "terminalSize":
                for console in self.consoleWidgets.values():
                    if console:
                        self.terminalSize = value
                        console.updateSizeHint(QSize(value, value))

    def _onProcessRunning(self, isRunning: bool) -> None:
        self.terminateAllButton.setEnabled(isRunning)
        self.processRunning = isRunning

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
            if self.processGen.canStart():
                self.processSubinterface.getProgressCard().start()
                self.threadManager.setProcessGenerator(self.processGen)
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

    def _onConsoleTextReceived(self, processID: int, text: str) -> None:
        self.consoleWidgets[processID].append(text)

    def _onClearConsole(self, processID: int) -> None:
        self.consoleWidgets[processID].clear()
