from PyQt6.QtCore import pyqtSignal

from typing import override
from app.components.console_view import ConsoleView
from module.concurrency.process.process_base import ProcessBase
from module.concurrency.thread.thread_manager import ThreadManager


class ThreadUIStreamer(ThreadManager):
    consoleTextStream = pyqtSignal(int, str)  # processID, text
    consoleCountChanged = pyqtSignal(list)  # list[int] # amount of new consoles
    clearConsole = pyqtSignal(int)  # processID

    def __init__(self, maxThreads: int, consoleWidgets: dict[int, ConsoleView]) -> None:
        super().__init__(maxThreads)
        self.consoleWidgets = consoleWidgets

        self.__connectSignalToSlot()

    def __connectSignalToSlot(self) -> None:
        self.consoleCountChanged.connect(self.__onConsoleCountChanged)
        self.threadClosed.connect(self.__onThreadClosed)

    def __onThreadClosed(self, processID: int) -> None:
        try:
            self.consoleWidgets[processID].activated.emit(False)
        except AttributeError:
            # The console widget with this PID was nuked
            pass

    def __onConsoleCountChanged(self, amount: list[int]) -> None:
        while amount:
            i = amount.pop()
            console = self.consoleWidgets[i]
            console.terminationRequest.connect(self._TerminateProcessRequest)

    def __setupProcessStream(
        self, processID: int, process: ProcessBase, setupConsole: bool
    ) -> None:
        if setupConsole:
            self.clearConsole.emit(processID)
            self.consoleWidgets[processID].activated.emit(True)

        process.consoleStream.connect(
            lambda text, processID=processID: self.consoleTextStream.emit(
                processID, text
            )
        )

    @override
    def _runProcesses(self) -> None:
        new_processes = super()._runProcesses()
        if new_processes:
            for threadID, isThreadNew, process in new_processes:
                self.__setupProcessStream(threadID, process, isThreadNew)
                thread = self._threadPool[threadID]
                thread.start()

    @override
    def _onProcessFinished(self, processID: int) -> None:
        new_processes = super()._onProcessFinished(processID)
        if new_processes:
            for threadID, isThreadNew, process in new_processes:
                self.__setupProcessStream(threadID, process, isThreadNew)
                thread = self._threadPool[threadID]
                thread.start()
