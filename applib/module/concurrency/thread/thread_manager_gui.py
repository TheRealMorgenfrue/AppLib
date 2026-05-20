from typing import override

from PyQt6.QtCore import pyqtSignal

from ....app.components.console_view import ConsoleView
from ..process.process_generator import ProcessGeneratorBase
from .thread_manager import ThreadManager


class ThreadManagerGui(ThreadManager):
    console_count_changed = pyqtSignal(list)
    """Emits whenever the console count has changed.

    Parameters
    ----------
    new_consoles : list[int]
        A list of `process_id`s reserved for the new consoles.
    """

    clear_console = pyqtSignal(int)
    """Clear text from the console widget with id `process_id`

    Parameters
    ----------
    process_id : int
    """

    def __init__(
        self,
        max_threads: int,
        ProcessGenerator: type[ProcessGeneratorBase],
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

    @override
    def _connect_signals_to_slots(self):
        super()._connect_signals_to_slots()
        self.console_count_changed.connect(self._on_console_count_changed)
        self.thread_removed.connect(self._on_thread_removed)

    def _on_thread_removed(self, process_id: int):
        console = self.console_widgets[process_id]
        if console:
            console.activated.emit(False)

    def _on_console_count_changed(self, amount: list[int]):
        while amount:
            i = amount.pop()
            console = self.console_widgets[i]
            if console:
                console.terminate_process.connect(self._terminate_thread)

    def _setup_process_stream(self, id: int):
        self.clear_console.emit(id)
        console = self.console_widgets[id]
        if console:
            console.activated.emit(True)
        else:
            self._logger.error(f"Process {id} is missing stream target", gui=True)

    @override
    def _run(self):
        new_processes = super()._run()
        for id in new_processes:
            self._setup_process_stream(id)
            self._thread_pool[id].start()

    @override
    def _on_process_success(self, id: int):
        match super()._on_process_success(id):
            case True:
                # New thread. Connect to GUI
                self._setup_process_stream(id)
            case False:
                # Old thread. Already connected
                self._logger.info("\n\n", log=False, pid=id)
                self._thread_pool[id].start()
            case None:
                # Thread is no longer in use
                pass
