from PyQt6.QtCore import pyqtSignal
from typing import override

from ....app.components.console_view import ConsoleView
from ..process.process_base import ProcessBase
from ..thread.thread_manager import ThreadManager


class ThreadUIStreamer(ThreadManager):
    consoleTextStream = pyqtSignal(int, str)  # process_id, text
    consoleCountChanged = pyqtSignal(list)  # list[int] # amount of new consoles
    clearConsole = pyqtSignal(int)  # process_id

    def __init__(
        self, max_threads: int, console_widgets: dict[int, ConsoleView]
    ) -> None:
        super().__init__(max_threads)
        self.console_widgets = console_widgets

        self.__connectSignalToSlot()

    def __connectSignalToSlot(self) -> None:
        self.consoleCountChanged.connect(self._onConsoleCountChanged)
        self.threadClosed.connect(self._onThreadClosed)

    def _onThreadClosed(self, process_id: int) -> None:
        try:
            self.console_widgets[process_id].activated.emit(False)
        except AttributeError:
            # The console widget with this PID was nuked
            pass

    def _onConsoleCountChanged(self, amount: list[int]) -> None:
        while amount:
            i = amount.pop()
            console = self.console_widgets[i]
            console.terminationRequest.connect(self._TerminateProcessRequest)

    def _setupProcessStream(
        self, process_id: int, process: ProcessBase, setupConsole: bool
    ) -> None:
        if setupConsole:
            self.clearConsole.emit(process_id)
            self.console_widgets[process_id].activated.emit(True)

        process.consoleStream.connect(
            lambda text, process_id=process_id: self.consoleTextStream.emit(
                process_id, text
            )
        )

    @override
    def _runProcesses(self) -> None:
        new_processes = super()._runProcesses()
        if new_processes:
            for threadID, isThreadNew, process in new_processes:
                self._setupProcessStream(threadID, process, isThreadNew)
                thread = self._thread_pool[threadID]
                thread.start()

    @override
    def _onProcessFinished(self, process_id: int) -> None:
        new_processes = super()._onProcessFinished(process_id)
        if new_processes:
            for threadID, isThreadNew, process in new_processes:
                self._setupProcessStream(threadID, process, isThreadNew)
                thread = self._thread_pool[threadID]
                thread.start()
