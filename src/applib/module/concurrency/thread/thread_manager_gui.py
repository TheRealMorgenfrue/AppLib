from typing import override

from PyQt6.QtCore import pyqtSignal

from ....app.components.console_view import ConsoleView
from ..process.process_generator import ProcessGenerator
from .thread_manager import ThreadManager


class ThreadManagerGui(ThreadManager):
    consoleCountChanged = pyqtSignal(list)
    """Emits whenever the console count has changed.

    Parameters
    ----------
    new_consoles : list[int]
        A list of `process_id`s reserved for the new consoles.
    """

    clearConsole = pyqtSignal(int)
    """Clear text from the console widget with id `process_id`

    Parameters
    ----------
    process_id : int
    """

    def __init__(
        self,
        max_threads: int,
        ProcessGenerator: type[ProcessGenerator],
        console_widgets: dict[int, ConsoleView | None],
    ):
        """
        A thread manager capable of redirecting output from processes
        in managed threads to GUI widgets.

        Parameters
        ----------
        max_threads : int
            Maximum size of the thread pool.
        console_widgets : dict[int, ConsoleView]
            A console-like widget with API support for thread managers.
        """
        super().__init__(max_threads, ProcessGenerator)
        self.console_widgets = console_widgets
        self.__connect_signal_to_slot()

    def __connect_signal_to_slot(self):
        self.consoleCountChanged.connect(self._on_console_count_changed)
        self.threadFinalized.connect(self._on_thread_finalized)

    def _on_thread_finalized(self, process_id: int):
        console = self.console_widgets[process_id]
        if console:
            console.activated.emit(False)

    def _on_console_count_changed(self, amount: list[int]):
        while amount:
            i = amount.pop()
            console = self.console_widgets[i]
            if console:
                console.terminate_process.connect(self._kill_process)

    def _setup_process_stream(self, thread_id: int):
        thread = self._thread_pool[thread_id]
        if not thread.isRunning():
            self.clearConsole.emit(thread_id)
            console = self.console_widgets[thread_id]
            if console:
                console.activated.emit(True)
            else:
                self._logger.error(
                    f"Missing output stream for thread {thread_id}", gui=True
                )
            thread.start()
        else:
            self._process_pool[thread_id].start.emit()

    @override
    def _run(self):
        new_processes = super()._run()
        for process_id in new_processes:
            self._setup_process_stream(process_id)

    @override
    def _on_process_finished(self, process_id: int):
        is_new_process = super()._on_process_finished(process_id)
        if is_new_process:
            self._setup_process_stream(process_id)
