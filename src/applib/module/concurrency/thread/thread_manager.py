import traceback
from enum import Enum

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from ...configuration.internal.core_args import CoreArgs
from ...logging import LoggingManager
from ..process.process_base import ProcessBase
from ..process.process_generator import ProcessGenerator


class ThreadManager(QObject):
    class State(Enum):
        Running = 10
        Stopped = 20

    ## Thread Pool Control ##
    updateMaxThreads = pyqtSignal(int)
    """Updates the maximum size of the thread pool.

    Parameters
    ----------
    max_threads : int
    """

    removeUnreservedThreads = pyqtSignal()
    """Removes unreserved thread IDs. Is related to `unreservedThreads`"""

    unreservedThreads = pyqtSignal(set)
    """Emits when a signal from `requestUnreservedThreads` is received.

    Parameters
    ----------
    thread_ids : list[int]
        The IDs of the unreserved threads.
    """

    threadFinalized = pyqtSignal(int)
    """Emits when a thread is no longer in use.

    Parameters
    ----------
    thread_id : int
        The ID of the finalized thread.
    """

    allThreadsFinalized = pyqtSignal()
    """Emits when all threads in the thread pool are finalized."""

    ## Process Control ##
    updateProcessGenerator = pyqtSignal(ProcessGenerator)
    """Updates the process generator

    Parameters
    ----------
    generator : ProcessGenerator
        An instance of a ProcessGenerator.
    """

    ## Execution Progress ##
    currentProgress = pyqtSignal(int)
    """Emits when current progress of the thread manager is changed.

    Parameters
    ----------
    new_progress : int
        The value of the progress.
    """

    totalProgress = pyqtSignal(int)
    """Emits when the total progress of the thread manager is changed.

    Parameters
    ----------
    new_progress : int
        The value of the progress.
    """

    ## Execution Control ##
    kill = pyqtSignal()
    """Emits when the thread manager should kill every process and thread immediately."""

    terminate = pyqtSignal()
    """Emits when the thread manager should terminate every process and thread gracefully."""

    start = pyqtSignal()
    """Start the thread manager"""

    changeState = pyqtSignal(State)
    """Emits whenever the thread manager changes state

    Parameters
    ----------
    state : ThreadManager.State
        The new state of the thread manager.
    """

    def __init__(self, max_threads: int, ProcessGenerator: type[ProcessGenerator]):
        """
        Base class for thread managers.

        The thread manager itself is running in a separate thread with its own QEvent loop.
        As such, all communication must be done using the signal/slot system.

        Parameters
        ----------
        max_threads : int
            The maximum size of the thread pool.
        """
        super().__init__()
        self._logger = LoggingManager()
        self._init = False

        # Threads
        self._thread_pool = {}  # type: dict[int, QThread]
        self._max_threads = max_threads
        self._threads_pending_removal = set()
        self._available_threads = set()

        # Processes
        self._process_pool = {}  # type: dict[int, ProcessBase]
        self._process_generator = ProcessGenerator()
        self._argument_generator = self._process_generator.args()
        self._argument_buffer = []  # type: list[list[str]]

        # Progress
        self._current_progress = 0  # Amount of processes that finished succesfully
        self._total_progress = 0  # The total amount of processes which will be executed

        # Execution Control
        self._killed = False
        self._terminated = False

    def __connect_signal_to_slot(self) -> None:
        # TODO: Implement by intercepting a user pressing the close button.
        # signalBus.appShutdown.connect(self._onAppShutdown)

        # Data Access
        self.removeUnreservedThreads.connect(self._on_remove_unreserved_threads)

        # Thread Control
        self.allThreadsFinalized.connect(self._on_all_threads_finalized)
        self.updateMaxThreads.connect(self._on_max_threads_updated)

        # Process Control
        self.updateProcessGenerator.connect(self._set_process_generator)

        # Execution Control
        self.kill.connect(self._kill_all)
        self.terminate.connect(self._terminate_all)
        self.start.connect(self._start)

    def _on_remove_unreserved_threads(self):
        thread_ids = self._available_threads
        self._available_threads.clear()
        for thread_id in thread_ids:
            self._threads_pending_removal.add(thread_id)
            self._finalize_thread(thread_id)

    def _on_max_threads_updated(self, max_threads: int):
        self._max_threads = max_threads
        if len(self._thread_pool) != 0:
            self._run()

    def _on_app_shutdown(self):
        self._terminate_all()

    def _thread_grammar(self, amount: int) -> str:
        return "threads" if amount != 1 else "thread"

    def _process_grammer(self, amount: int) -> str:
        return "processes" if amount != 1 else "process"

    def _kill_all(self):
        if self._killed:
            return

        self._killed = True
        self._logger.info("Killing all processes")
        for thread_id in self._thread_pool.keys():
            self._kill_process(thread_id)

    def _kill_process(self, process_id: int):
        self._process_pool[process_id].kill.emit()

    def _terminate_all(self) -> None:
        if self._terminated:
            return

        self._terminated = True
        self._logger.info("Terminating all processes")
        for thread_id in self._thread_pool.keys():
            self._terminate_process(thread_id)

    def _terminate_process(self, process_id: int):
        self._process_pool[process_id].terminate.emit()

    def _run(self) -> list[int]:
        """Schedule processes for execution in all available threads.

        Note
        ----
        This method is meant to be overridden in a child class and called with
        super() to perform child-specific process/thread setup.

        Returns
        -------
        list[int]
            A list of process IDs for the new processes.
        """
        self._update_thread_pool()
        process_ids = []
        for thread_id in list(self._available_threads):
            if self._create_process(thread_id) is not None:
                process_ids.append(thread_id)
                self._available_threads.remove(thread_id)
        return process_ids

    def _on_process_finished(self, process_id: int) -> bool:
        """Runs a new process with ID `process_id`, if possible.

        Note
        ----
        - This method is meant to be overridden in a child class and called with
        super() to perform the new process/thread setup.
        - Remember to start the new thread in the child class!

        Parameters
        ----------
        process_id : int
            The ID of the process that just finished.

        Returns
        -------
        bool
            Returns True if a new process is created.
        """
        if (
            not (self._terminated or self._killed)
            and self._current_progress < self._total_progress
        ):
            self._current_progress += 1  # TODO: CurrentProgress does not account for a process terminated manually (using its 'Terminate' button)
            self.currentProgress.emit(self._current_progress)

            if process_id not in self._threads_pending_removal:
                new_proc = self._create_process(process_id)
                if new_proc is not None:
                    return True
        self._finalize_process(process_id)
        return False

    def _on_process_failed(self, process_id: int):
        # TODO: Save progress. Show a list of failed processes and the reasons in the GUI
        # TODO: Track process' download progress and save upon failure, to allow easy recovery
        process = self._process_pool[process_id]
        self._argument_buffer.append(process.args)
        self._logger.warning(
            f"Process {process_id} failed",
            title="Process failure",
            gui=True,
            pid=process_id,
        )
        self._on_process_finished(process_id)

    def _create_process(self, process_id: int) -> ProcessBase | None:
        """Creates a new process with ID `process_id` and assigns it
        to the thread with the same ID.

        Parameters
        ----------
        process_id : int
            The ID of the new process.

        Returns
        -------
        ProcessBase | None
            The new process or None if a process could not be created.
        """
        try:
            args = self._argument_buffer.pop()
        except IndexError:
            args = next(self._argument_generator, None)

        if args is not None:
            is_running = False
            try:
                process = self._process_pool[process_id]
            except KeyError:
                process = self._process_generator.process()()
                process.finished.connect(self._on_process_finished)
                process.failed.connect(self._on_process_failed)
                self._process_pool[process_id] = process
                thread = self._thread_pool[process_id]
                process.moveToThread(thread)
                thread.started.connect(process._start)
                is_running = not thread.isRunning()

            process.setProgram(self._process_generator.program())
            process.setArguments(args)
            process.process_id = process_id

            if len(self._process_pool) == 1 and is_running:
                self.changeState.emit(ThreadManager.State.Running)
            return process

    def _finalize_process(self, process_id: int):
        """Performs cleanup after a process has finished.
        The process is removed from the process pool.

        Parameters
        ----------
        process_id : int
            The ID of the finished process.
        """
        # Ensure a process is only finalized once
        if process_id not in self._process_pool:
            return

        self._process_pool.pop(process_id)
        self._thread_pool[process_id].quit()

    def _create_thread(self, thread_id: int) -> QThread:
        """Creates a new thread and returns it.

        Parameters
        ----------
        thread_id : int
            The ID of the new thread.
        """
        self._logger.debug(f"Creating thread {thread_id}")
        self._thread_pool[thread_id] = thread = QThread()
        thread.finished.connect(
            lambda thread_id=thread_id: self._finalize_thread(thread_id)
        )
        return thread

    def _finalize_thread(self, thread_id: int) -> None:
        """Performs cleanup after a thread has finished.
        The thread is removed from the thread pool.

        Parameters
        ----------
        thread_id : int
            The ID of the finished thread.
        """
        # Ensure a thread is only finalized once
        if thread_id not in self._thread_pool:
            return

        self._logger.debug(f"Finalizing thread {thread_id}")
        self._thread_pool.pop(thread_id)

        try:
            self._threads_pending_removal.remove(thread_id)
        except KeyError:
            pass

        self.threadFinalized.emit(thread_id)

        if not self._thread_pool:
            self.allThreadsFinalized.emit()

    def _update_thread_pool(self):
        """Compute the active thread count and schedule threads accordingly."""
        about_to_finish = (
            self._current_progress + self._max_threads > self._total_progress
        )
        just_getting_started = self._current_progress == 0

        if not about_to_finish or just_getting_started:
            thread_difference = (
                (self._max_threads - len(self._thread_pool))
                if self._max_threads <= self._total_progress
                else self._total_progress - len(self._thread_pool)
            )

            # Thread count is increased
            if thread_difference > 0:
                start = len(self._thread_pool)
                stop = start + thread_difference
                for i in range(start, stop):
                    self._available_threads.add(i)
                    self._thread_pool[i] = self._create_thread(i)
                self._logger.debug(
                    f"Added {thread_difference} {self._thread_grammar(thread_difference)} to the thread pool "
                    + f"(total size: {len(self._thread_pool)})"
                )

            # Thread count is decreased
            elif thread_difference < 0:
                start = max(self._thread_pool.keys())
                stop = (
                    start + thread_difference
                )  # Addition cause the difference is negative
                step = -1
                for thread_id in range(start, stop, step):
                    self._threads_pending_removal.add(thread_id)
                removed_threads = stop - start
                if removed_threads > 0:
                    self._logger.debug(
                        f"Removed {removed_threads} {self._thread_grammar(removed_threads)} from the thread pool "
                        + f"(total size: {len(self._thread_pool)})"
                    )

    def _on_all_threads_finalized(self) -> None:
        if self._terminated:
            self._logger.info(
                f"Termination successful. Finished {self._current_progress} / {self._total_progress} processes"
            )
        elif self._current_progress < self._total_progress:
            self._logger.warning(
                f"Some processes did not complete. Missing {self._total_progress - self._current_progress} / {self._total_progress} processes"
            )
        else:
            self._logger.info(
                f"{f"All {self._total_progress} processes have" if self._total_progress != 1 else "The process has"} finished!"
            )
        self.changeState.emit(ThreadManager.State.Stopped)

    def _set_process_generator(self, generator: ProcessGenerator):
        self._process_generator = generator

    def _start(self) -> None:
        if not self._init:
            self.__connect_signal_to_slot()
            self._init = True

        if not self._process_generator.can_start():
            self._logger.error(f"No arguments available", gui=True)
            return

        self._killed = False
        self._terminated = False
        self._current_progress = 0
        try:
            self._argument_generator = self._process_generator.args()
            self._total_progress = self._process_generator.get_total_progress()
            self._logger.info(
                f"Initializing {self.__class__.__name__}. Processes to execute: {self._total_progress}"
            )
            self.currentProgress.emit(self.currentProgress)
            self.totalProgress.emit(self._total_progress)

            self._run()

            thread_pool_size = len(self._thread_pool)
            self._logger.debug(
                f"Scheduled {self._total_progress} {self._process_grammer(self._total_progress)} "
                + f"in {thread_pool_size} {self._thread_grammar(thread_pool_size)}"
            )
        except Exception:
            self._logger.critical(
                f"{self.__class__.__name__} has failed\n"
                + traceback.format_exc(limit=CoreArgs._core_traceback_limit),
                gui=True,
            )
            self._terminate_all()
