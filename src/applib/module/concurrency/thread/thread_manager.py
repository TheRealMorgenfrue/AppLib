from typing import Any, Generator, Optional
from PyQt6.QtCore import QThread, pyqtSignal

import traceback

from ..process.process_base import ProcessBase
from ..process.process_generator import ProcessGenerator
from ...config.internal.core_args import CoreArgs
from ...logging import AppLibLogger
from ...tools.utilities import iterToString


# A subclassed QThread has no event loop per default
# As such, it cannot receive any pyqtSignals, only emit
# An eventloop can be instantiated by calling exec(), however, this call is thread blocking
class ThreadManager(QThread):
    """
    Base class for Thread Managers.

    The Thread Manager itself is running in a separate thread with its own QEvent loop.
    As such, all communication must be done using the signal/slot system.
    """

    _logger = AppLibLogger().getLogger()

    updateMaxThreads = pyqtSignal(int)
    threadsRemoved = pyqtSignal(list)  # list of threadIDs safe for removal
    currentProgress = pyqtSignal(int)
    totalProgress = pyqtSignal(int)

    kill = pyqtSignal(bool)  # Include self: True/False
    threadClosed = pyqtSignal(int)  # process_id
    allThreadsClosed = pyqtSignal()

    def __init__(self, max_threads: int) -> None:
        super().__init__()
        self.name = "thread manager"
        self.max_threads = max_threads

        self._current_progress = 0  # Amount of processes that finished succesfully
        self._total_progress = 0  # The total amount of processes which will be executed
        self._process_gen = None  # type: ProcessGenerator
        self._genIter = None  # type: Generator[ProcessBase, Any, Any]
        self._process_pool = []  # type: list[ProcessBase]
        self._thread_pool = {}  # type: dict[int, QThread]
        self._stop = False  # Don't create new processes
        self._killed = False

        self.__connectSignalToSlot()  # This will execute in the correct thread since this class is subclassing QThread

    def __connectSignalToSlot(self) -> None:
        # TODO: Implement with a hideEvent() instead
        # signalBus.appShutdown.connect(self._onAppShutdown)
        self.kill.connect(self._TerminateAllRequest)
        self.allThreadsClosed.connect(self._onAllThreadsClosed)
        self.updateMaxThreads.connect(self._onMaxThreadsUpdated)

    def _onMaxThreadsUpdated(self, maxThreads: int) -> None:
        self.max_threads = maxThreads
        if self._total_progress != 0:
            # Update thread/process pool
            self._runProcesses()

    def _onAppShutdown(self) -> None:
        self._TerminateAllRequest(suicide=True)

    def _threadGrammar(self, amount: int) -> str:
        return "threads" if amount != 1 else "thread"

    def _processGrammer(self, amount: int) -> str:
        return "processes" if amount != 1 else "process"

    def _TerminateAllRequest(self, suicide: bool) -> None:
        try:
            still_alive = []
            self._stop = True
            self._killed = suicide
            self._logger.info("Terminating all processes")
            for threadID in self._thread_pool.keys():
                if not self._TerminateProcessRequest(threadID):
                    still_alive.append(threadID)
            length = len(still_alive)
            if length > 0:
                self._logger.warning(
                    f"Process {iterToString(still_alive, separator=", ")} {'are' if length > 1 else ' is'} still alive"
                )
        except Exception:
            self._logger.critical("Process termination failed catastrophically!")

    def _TerminateProcessRequest(self, process_id: int) -> bool:
        try:
            process = self._process_pool[process_id]
            if process:
                self._logger.info(f"Terminating process {process_id}")
                process.terminate()
            return True
        except Exception:
            self._logger.error(
                f"Failed to properly terminate process {process_id}\n"
                + traceback.format_exc(limit=CoreArgs._core_traceback_limit)
            )
            return False

    def _runProcesses(self) -> list[tuple[int, bool, ProcessBase]]:
        """Schedule all processes for execution in available threads

        Note
        ----
        This method is meant to be overridden in a child class and called with
        super() to perform child-specific process/thread setup.

        Returns
        -------
        list[tuple[int, bool, ProcessBase]]
            tuple[0] : int
                The threadID of the available thread (which is now being reserved by a new process).

            tuple[1] : bool
                Is the thread newly created (i.e. only essential setup has been made).

            tuple[2] : ProcessBase
                A subclass of ProcessBase. This is the process that will run in the thread with threadID.
        """
        isRunning = len(self._thread_pool)

        if not isRunning:
            self._total_progress = self._process_gen.getTotalProgress()
            self._logger.info(
                f"Initializing {self.name}. Processes to execute: {self._total_progress}"
            )
            self.currentProgress.emit(self.currentProgress)
            self.totalProgress.emit(self._total_progress)

        # Populate thread pool and process pool
        availableThreads = self._updateThreadPool()
        new_processes = self._createProcesses(availableThreads)

        if not isRunning:
            threadPoolSize = len(self._thread_pool)
            self._logger.debug(
                f"Scheduled {self._total_progress} {self._processGrammer(self._total_progress)} "
                + f"in {threadPoolSize} {self._threadGrammar(threadPoolSize)}"
            )
        return new_processes

    def _onProcessFinished(
        self, process_id: int
    ) -> list[tuple[int, bool, ProcessBase]] | None:
        """Schedules an amount of processes to run in a thread based on available threads.
        New processes are taken from the process generator.

        Note
        ----
        - This method is meant to be overridden in a child class and called with
        super() to perform the new process/thread setup.
        - Remember to start the new thread in the child class!
        - The process should delete itself after being terminated or finishes. Thus, it is not done in this method.

        Parameters
        ----------
        process_id : int
            The ID of the process that just finished.

        Returns
        -------
        list[tuple[int, bool, ProcessBase]] | None
            tuple[0] : int
                The threadID of the available thread (which is now being reserved by a new process).

            tuple[1] : bool
                Is the thread newly created (i.e. only essential setup has been made).

            tuple[2] : ProcessBase
                A subclass of ProcessBase. This is the process that will run in the thread with threadID.

        Returns None if no threads are availble to run a new process.
        """
        try:
            # Delete old thread
            thread = self._thread_pool[process_id]
            thread.quit()
            thread.wait()
            thread.deleteLater()  # TODO: Recycle threads instead of deleting them for each process (figure out why signals/slots cause issues with recycled threads)
            self._thread_pool[process_id] = None

            # Only attempt create new threads if allowed
            if not self._stop:
                self._current_progress += 1  # TODO: CurrentProgress does not account for a process terminated manually (using its 'Terminate' button)
                self.currentProgress.emit(self._current_progress)

                availableThreads = self._updateThreadPool(process_id)

                if availableThreads:
                    new_processes = self._createProcesses(availableThreads)
                    if new_processes:
                        return new_processes

            # Thread is no longer in use (threadID and process_id are identical here)
            self._closeThread(process_id)
        except Exception:
            self._logger.error(
                f"{self.name.title()} has failed\n"
                + traceback.format_exc(limit=CoreArgs._core_traceback_limit)
            )
            self.kill.emit(True)

    def _createProcesses(
        self, availableThreads: list[tuple[int, bool]]
    ) -> list[tuple[int, bool, ProcessBase]]:
        """Creates a new process for each available thread in *availableThreads*.\n
        The process_id of the newly created process matches the threadID of the thread.

        Parameters
        ----------
        availableThreads : list[tuple[int, bool]]
            tuple[0] : int
                The threadID of an available thread.

            tuple[1] : bool
                Whether this thread has just been created (i.e. only essential setup has been made).

        Returns
        -------
        list[tuple[int, bool, ProcessBase]]
            tuple[0] : int
                The threadID of the available thread (which is now being reserved by a new process).

            tuple[1] : bool
                Is the thread newly created (i.e. only essential setup has been made).

            tuple[2] : ProcessBase
                A subclass of ProcessBase. This is the process that will run in the thread with threadID.
        """
        new_processes = []  # type: list[tuple[QThread, ProcessBase]]
        for threadID, isThreadNew in availableThreads:
            process = next(self._genIter, None)
            if process:
                self._logger.debug(f"Starting new thread with ID {threadID}")
                self._process_pool[threadID] = process
                self._thread_pool[threadID] = thread = QThread()
                process.setProcessID(threadID)
                process.moveToThread(thread)
                process.finished.connect(self._onProcessFinished)
                process.failed.connect(
                    self._onProcessFinished
                )  # TODO: Track process' download progress and save upon failure, to allow easy recovery
                thread.started.connect(process.start)
                new_processes.append((threadID, isThreadNew, process))
        return new_processes

    def _closeThread(self, threadID: int) -> None:
        """Tell everyone that this threadID is no longer in use.

        However, a new thread with the same threadID may be created later.

        Parameters
        ----------
        threadID : int
            Close the thread with this threadID.
        """
        # Ensure a thread is only closed once
        if threadID not in self._thread_pool:
            return

        self._logger.debug(f"Closing thread {threadID}")
        self._thread_pool.pop(threadID)
        self.threadClosed.emit(threadID)
        if not self._thread_pool:
            self.allThreadsClosed.emit()

    def _updateThreadPool(
        self, finishedProcessID: Optional[int] = None
    ) -> list[tuple[int, bool]]:
        """Compute the active thread count and schedule threads accordingly
        by opening/closing threads in the thread pool.

        Parameters
        ----------
        finishedProcessID : Optional[int], optional
            The process_id of the most recently finished process.
            By default `None`.

        Returns
        -------
        list[tuple[int, bool]]
            A list of all available threads.

            tuple[0] : int
                The threadID of an available thread.

            tuple[1] : bool
                Whether this thread has just been created (i.e. only essential setup has been made).
        """
        availableThreads = []
        addFinishedProcessID = True
        aboutToFinish = self._current_progress + self.max_threads > self._total_progress
        justGettingStarted = self._current_progress == 0

        if not aboutToFinish or justGettingStarted:
            threadDifference = (
                (self.max_threads - len(self._thread_pool))
                if self.max_threads <= self._total_progress
                else self._total_progress - len(self._thread_pool)
            )

            # Thread count is increased
            if threadDifference > 0:
                start = len(self._thread_pool)
                stop = start + threadDifference
                for i in range(start, stop):
                    availableThreads.append((i, True))
                    self._thread_pool |= {i: None}
                    self._process_pool.append(None)
                self._logger.debug(
                    f"Added {threadDifference} {self._threadGrammar(threadDifference)} to the thread pool "
                    + f"(total size: {len(self._thread_pool)})"
                )

            # Thread count is decreased
            elif threadDifference < 0:
                removedThreadIDs = []
                start = max(self._thread_pool.keys())
                stop = (
                    start + threadDifference
                )  # Addition cause the difference is negative
                step = -1
                for threadID in range(start, stop, step):
                    # Ensure the threadID exists and is safe to remove
                    if (
                        threadID in self._thread_pool
                        and self._thread_pool[threadID] is None
                    ):
                        # if self._threadPool[threadID] is None: # Thread removal testing only (will explode)!
                        self._closeThread(threadID)
                        removedThreadIDs.append(threadID)
                removedThreads = len(removedThreadIDs)
                if removedThreads:
                    self._logger.debug(
                        f"Removed {removedThreads} {self._threadGrammar(removedThreads)} from the thread pool "
                        + f"(total size: {len(self._thread_pool)})"
                    )
                    self.threadsRemoved.emit(removedThreadIDs)
                    addFinishedProcessID = finishedProcessID not in removedThreadIDs

        if addFinishedProcessID and finishedProcessID is not None:
            availableThreads.append((finishedProcessID, False))
        return availableThreads

    def _onAllThreadsClosed(self) -> None:
        try:
            if self._stop:
                self._logger.info(
                    f"Termination successful. Finished {self._current_progress} / {self._total_progress} processes"
                )
                return

            if self._current_progress < self._total_progress:
                missing = self._total_progress - self._current_progress
                self._logger.warning(
                    f"Some processes did not complete. Missing {missing} / {self._total_progress} processes"
                )
            else:
                self._logger.info(
                    f"{f"All {self._total_progress} processes have" if self._total_progress != 1 else "The process has"} finished!"
                )
        finally:
            self.quit()
            if self._killed:
                self.deleteLater()

    def setProcessGenerator(self, generator: ProcessGenerator) -> None:
        """The process generator supplies the Thread Manager with
        ProcessBase instances to run in separate threads.

        Parameters
        ----------
        generator : ProcessGenerator
            A subclass of *ProcessGenerator* that creates ProcessBase instances.
        """
        self._process_gen = generator
        self._genIter = self._process_gen.generator()

    def run(self) -> None:
        try:
            self._runProcesses()
            # Create event loop in subclassed QThread. Thread blocking
            self.exec()
        except Exception:
            self._logger.critical(
                f"{self.name.title()} has failed\n"
                + traceback.format_exc(limit=CoreArgs._core_traceback_limit)
            )
            # Call terminate method directly as the event loop is not running at this point
            self._TerminateAllRequest(suicide=True)
        finally:
            # Resetting values to prevent previus process executions from interfering with the current execution
            # (as a new thread manager is not instantiated per run)
            self._stop, self._killed = False, False
            self._current_progress, self._total_progress = 0, 0
