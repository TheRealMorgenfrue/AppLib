import traceback
from enum import Enum
from typing import Iterator, override

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from ...configuration.internal.core_args import CoreArgs
from ...logging import LoggingManager
from ..process.process_base import ProcessGUI
from ..process.process_generator import ProcessGeneratorBase


class ThreadManager(QObject):
    """
    ## Thread Classes

    - Max threads
        The total amount of threads managed.

    - Available threads
        Threads currently idle.

    - Running threads
        Threads busy doing work.

    - Deallocated threads
        Threads scheduled for removal once their work is done.
    """

    class State(Enum):
        Starting = 0
        Running = 10
        Stopped = 20
        Terminated = 30
        Killed = 40

    ## Thread Pool Control ##
    thread_removed = pyqtSignal(int)
    """Emits when a thread is no longer in use.

    Parameters
    ----------
    id : int
        The ID of the thread.
    """

    all_threads_removed = pyqtSignal()
    """Emits when all threads in the thread pool are finalized."""

    ## Process Control ##
    update_process_generator = pyqtSignal(ProcessGeneratorBase)
    """Updates the process generator

    Parameters
    ----------
    generator : ProcessGenerator
        An instance of a ProcessGenerator.
    """

    ## Execution Progress ##
    current_progress = pyqtSignal(int)
    """Emits when current progress of the thread manager is changed.

    Parameters
    ----------
    new_progress : int
        The value of the progress.
    """

    total_progress = pyqtSignal(int)
    """Emits when the total progress of the thread manager is changed.

    Parameters
    ----------
    new_progress : int
        The value of the progress.
    """

    ## Execution Control ##
    kill_all = pyqtSignal()
    """Emits when the thread manager should kill every process and thread immediately."""

    terminate_all = pyqtSignal()
    """Emits when the thread manager should terminate every process and thread gracefully."""

    change_state = pyqtSignal(State)
    """Emits whenever the thread manager changes state

    Parameters
    ----------
    state : ThreadManager.State
        The new state of the thread manager.
    """

    def __init__(self, max_threads: int, ProcessGenerator: type[ProcessGeneratorBase]):
        """
        Base class for thread managers.

        Parameters
        ----------
        max_threads : int
            The maximum size of the thread pool.
        """
        super().__init__()
        self._logger = LoggingManager()
        self._connected = False

        # Threads
        self._thread_pool = {}  # type: dict[int, QThread]
        self._max_threads = abs(max_threads)
        self._deallocated_threads = set()  # type: set[int]
        self._available_threads = set()  # type: set[int]

        # Processes
        self._process_pool = {}  # type: dict[int, ProcessGUI]
        self._process_generator = ProcessGenerator()
        self._process_args = None  # type: Iterator[str]
        self._argument_buffer = []  # type: list[list[str]]

        # Progress
        self._current_progress = 0  # Amount of processes that finished succesfully
        self._total_progress = 0  # The total amount of processes which will be executed

        # Execution Control
        self._state = ThreadManager.State.Starting

    @property
    def max_threads(self):
        """The maximum size of the thread pool"""
        return self._max_threads

    @max_threads.setter
    def max_threads(self, threads: int):
        self._max_threads = abs(threads)
        if len(self._thread_pool) != 0 and self._state == ThreadManager.State.Running:
            self._run()

    def __str__(self):
        ac = len(self._thread_pool)
        av = len(self._available_threads)
        dt = len(self._deallocated_threads)
        return (
            f"active: {ac}, available: {av-ac}, deallocated: {dt}, pool size: {ac+av}"
        )

    def __set_state(self, state: "ThreadManager.State"):
        self._logger.debug(
            f"{self.__class__.__name__} state: {state.name.capitalize()}"
        )
        self._state = state
        self.change_state.emit(state)

    def _connect_signals_to_slots(self) -> None:
        # Thread Control
        self.all_threads_removed.connect(self._on_work_complete)

        # Process Control
        self.update_process_generator.connect(self._on_process_generator_updated)

        # Execution Control
        self.kill_all.connect(self._kill_all)
        self.terminate_all.connect(self._terminate_all)

    def _thread_grammar(self, amount: int) -> str:
        return "threads" if amount != 1 else "thread"

    def _process_grammar(self, amount: int) -> str:
        return "processes" if amount != 1 else "process"

    def _kill_all(self):
        if self._state == ThreadManager.State.Killed:
            return

        self.__set_state(ThreadManager.State.Killed)
        self._logger.info("Killing all processes")
        for thread in self._thread_pool.values():
            # Not calling _kill_thread here as we don't care about waiting
            thread.terminate()

    def _terminate_all(self):
        if self._state == ThreadManager.State.Terminated:
            return

        self.__set_state(ThreadManager.State.Terminated)
        self._logger.info("Terminating all processes")
        for thread in self._thread_pool.values():
            # Not calling _terminate_thread here as we don't care about waiting
            thread.quit()

    def _kill_thread(self, id: int):
        try:
            thread = self._thread_pool[id]
            self._logger.debug(f"Killing thread {id}")
            thread.terminate()
            thread.wait()
        except KeyError:
            self._logger.warning(f"Thread {id} not found")

    def _terminate_thread(self, id: int):
        try:
            thread = self._thread_pool[id]
            self._logger.debug(f"Terminating thread {id}")
            thread.quit()
            thread.wait()
        except KeyError:
            self._logger.warning(f"Thread {id} not found")

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
        thread_ids = []
        for id in list(self._available_threads):
            if self._create_thread(id) is not None:
                thread_ids.append(id)
                self._available_threads.remove(id)
        return thread_ids

    def _on_process_finished(self, id: int, returncode: tuple[int | None]):
        (code,) = returncode
        if code == 0:
            self._on_process_success(id)
        elif code is None:
            # Process still running! This shouldn't happen
            self._logger.error(
                f"Process {id} finished without exit code (it's still running)"
            )
        else:
            self._on_process_failed(id)

    def _on_process_success(self, id: int) -> bool | None:
        """Runs a new process with ID `id`, if possible.

        Note
        ----
        - This method is meant to be overridden in a child class and called with
        super() to perform the new process/thread setup.
        - Remember to start the new thread in the child class!

        Parameters
        ----------
        id : int
            The ID of the process that just finished.

        Returns
        -------
        bool | None
            Is True if `id` is not present in the thread pool and False otherwise.
            Is None if `id` is not in use.
        """
        if (
            not (
                self._state == ThreadManager.State.Terminated
                or self._state == ThreadManager.State.Killed
            )
            and self._current_progress < self._total_progress
        ):
            self._current_progress += 1  # TODO: CurrentProgress does not account for a process terminated manually (using its 'Terminate' button)
            self.current_progress.emit(self._current_progress)

            if id not in self._deallocated_threads:
                return self._create_thread(id)

        self._remove_thread(id)

    def _on_process_failed(self, id: int) -> bool:
        # TODO: Save progress. Show a list of failed processes and the reasons in the GUI
        # TODO: Track process' download progress and save upon failure, to allow easy recovery
        # process = self._process_pool[id]
        # self._argument_buffer.append(process.args)
        return self._on_process_success(id)

    def _create_thread(self, id: int) -> bool:
        """Creates a new process with ID `id` and assigns it
        to the thread with the same ID.

        Parameters
        ----------
        id : int
            The ID of the new process.

        Returns
        -------
        bool
            Is True if `id` is not present in the thread pool and False otherwise.
        """
        try:
            args = self._argument_buffer.pop()
        except IndexError:
            args = next(self._process_args, None)

        is_new_thread = False
        if args is not None:
            try:
                thread = self._thread_pool[id]
                # Delete the thread previously using `id`.
                if thread.isRunning():
                    thread.quit()
                    thread.wait()
                    thread.deleteLater()
            except KeyError:
                is_new_thread = True

            thread = self._process_generator.process()(
                pid=id,
                program=self._process_generator.program(),
                args=args,
            )
            self._thread_pool[id] = thread
            thread.done.connect(self._on_process_finished)

            if len(self._thread_pool) == 1 and not thread.isRunning():
                self.__set_state(ThreadManager.State.Running)

        return is_new_thread

    def _remove_thread(self, id: int):
        """Removes a thread from the thread pool.

        Parameters
        ----------
        id : int
            The ID of the thread.
        """
        if id in self._thread_pool:
            self._logger.debug(f"Removing thread {id}")
            thread = self._thread_pool[id]
            if thread.isRunning():
                self._terminate_thread(id)

            self._thread_pool.pop(id).deleteLater()
            self.thread_removed.emit(id)

            if len(self._thread_pool) == 0:
                self.all_threads_removed.emit()

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
                self._logger.debug(
                    f"Added {thread_difference} {self._thread_grammar(thread_difference)} ({self})"
                )

            # Thread count is decreased
            elif thread_difference < 0:
                start = max(self._thread_pool.keys())
                stop = (
                    start + thread_difference
                )  # Addition cause the difference is negative
                step = -1
                for id in range(start, stop, step):
                    self._deallocated_threads.add(id)
                removed_threads = stop - start
                if removed_threads > 0:
                    self._logger.debug(
                        f"Deallocated {removed_threads} {self._thread_grammar(removed_threads)} ({self})"
                    )

    def _clean_thread_pool(self):
        for thread in self._thread_pool.values():
            if thread.isRunning():
                thread.quit()
                thread.wait()
            thread.deleteLater()
        self._thread_pool.clear()

    def _on_work_complete(self):
        if self._current_progress < self._total_progress:
            self._logger.warning(
                f"Some processes did not complete. Missing {self._total_progress - self._current_progress} / {self._total_progress} processes"
            )
        else:
            self._logger.info(
                f"Finished {self._current_progress} / {self._total_progress} processes"
            )
        self._clean_thread_pool()
        self.__set_state(ThreadManager.State.Stopped)

    def _on_process_generator_updated(self, generator: ProcessGeneratorBase):
        self._process_generator = generator

    def start(self):
        try:
            if not self._connected:
                self._connect_signals_to_slots()
                self._connected = True

            self.__set_state(ThreadManager.State.Starting)
            args = self._process_generator.arguments_list()

            self._current_progress = 0
            self._total_progress = len(args)

            if self._total_progress == 0:
                self._logger.error(f"No arguments available", gui=True)
                return

            self._process_args = iter(args)

            self._logger.info(
                f"Initializing {self.__class__.__name__}. Processes to execute: {self._total_progress}"
            )
            self.current_progress.emit(self.current_progress)
            self.total_progress.emit(self._total_progress)

            self._run()

            thread_pool_size = len(self._thread_pool)
            self._logger.info(
                f"Scheduled {self._total_progress} {self._process_grammar(self._total_progress)} "
                + f"in {thread_pool_size} {self._thread_grammar(thread_pool_size)}"
            )
        except Exception:
            self._logger.critical(
                f"{self.__class__.__name__} has failed\n"
                + traceback.format_exc(limit=CoreArgs._core_traceback_limit),
                gui=True,
            )
            self._terminate_all()
