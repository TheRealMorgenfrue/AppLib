import asyncio
import os
import shlex
import signal
import sys
import traceback
from asyncio import subprocess
from enum import Enum
from typing import IO, Any, override

import qasync
from PyQt6.QtCore import QDeadlineTimer, QThread, pyqtSignal

from ...configuration.internal.core_args import CoreArgs
from ...logging import LoggingManager


class ProcessStatus(Enum):
    PAUSED = 0
    TERMINATED = 1
    KILLED = 2
    RUNNING = 4
    STARTING = 5


# Signals must not be connected to slots in __init__
# as that will result in them being bound to the main thread.
# (a good idea would be to connect signals in the "run" method instead).
#
# A subclassed QThread has no event loop per default.
# As such, it cannot receive any pyqtSignals, only emit.
# An eventloop can be instantiated by calling exec(), however, this call is thread blocking.
class CoreProcess(QThread):
    """The basic process which doesn't capture it's output"""

    done = pyqtSignal(int, tuple)
    """The process has finished.

    Parameters
    ----------
    process_id : int
        The id of the process.
    returncode : tuple[int | None]
        The exit code of the process
    """
    pause = pyqtSignal()
    """Suspend the process."""

    resume = pyqtSignal()
    """Continue the process."""

    pipe_closed = pyqtSignal()
    """Indicates process has finished"""

    def __init__(self, pid: int, program: str, args: str):
        """The base class for processes.

        NOTE: All communication with the process should be made using the signal/slot system.

        Parameters
        ----------
        pid : int
            The process' ID.
        program : str
            The program to run.
        args : str
            The arguments to run `program` with.
        """
        super().__init__()
        self._event_loop = None
        self._logger = LoggingManager()
        self._status = ProcessStatus.STARTING
        self.process: asyncio.subprocess.Process = None
        self.pid = pid
        self.program = program
        self.args = args

    def __connectSignalToSlot(self):
        self.pause.connect(self._pause)
        self.resume.connect(self._resume)
        self.pipe_closed.connect(self._onProcessFinished)

    def _onProcessFinished(self):
        returncode_msg = f"(code {self.process.returncode})"

        match self._status:
            case ProcessStatus.PAUSED:
                self._logger.error(
                    f"Process {self.pid} finished in paused state {returncode_msg}",
                    gui=True,
                )
            case ProcessStatus.TERMINATED:
                self._logger.debug(f"Process {self.pid} terminated {returncode_msg}")
            case ProcessStatus.KILLED:
                self._logger.debug(f"Process {self.pid} killed {returncode_msg}")
            case ProcessStatus.RUNNING:
                if self.process.returncode == 0:
                    self._logger.debug(f"Process {self.pid} finished {returncode_msg}")
                elif self.process.returncode is None:
                    # Process is still running
                    pass
                else:
                    self._logger.debug(f"Process {self.pid} failed {returncode_msg}")
            case ProcessStatus.STARTING:
                self._logger.error(
                    f"Process {self.pid} finished in starting state {returncode_msg}",
                    gui=True,
                )
        self.done.emit(self.pid, (self.process.returncode,))

    async def _kill_process(self):
        self._logger.info(f"\nKilling process {self.pid}", log=False, pid=self.pid)
        self._status = ProcessStatus.KILLED

        try:
            self.process.kill()
        except ProcessLookupError:
            # Already dead
            pass

    def _terminate_process(self):
        self._logger.info(f"\nTerminating process {self.pid}", log=False, pid=self.pid)
        self._status = ProcessStatus.TERMINATED

        try:
            self.process.terminate()
        except ProcessLookupError:
            # Already dead
            pass

    def _pause(self):
        self._logger.info(f"\nPausing process {self.pid}", log=False, pid=self.pid)
        self._status = ProcessStatus.PAUSED
        self.process.send_signal(signal.SIGSTOP)

    def _resume(self):
        self._logger.info(f"\nResuming process {self.pid}", log=False, pid=self.pid)
        self._status = ProcessStatus.RUNNING
        self.process.send_signal(signal.SIGCONT)

    async def _run(self) -> None:
        kwargs = {}

        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

            kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE
            kwargs["startupinfo"] = startupinfo

        self.process = await asyncio.create_subprocess_exec(
            self.program,
            *shlex.split(self.args),
            stdout=self.stdout(),
            stderr=self.stderr(),
            env=self.env(),
            **kwargs,
        )

        self._status = ProcessStatus.RUNNING

        self._logger.debug(
            f'Process {self.pid} started\n\tProgram: "{self.program}"\n\tArgs: "{self.args}"'
        )
        await self.process_monitor()

    async def process_monitor(self):
        """Monitor the process.

        What "monitor" means is up to the implementation of this method.
        By default, wait until the process exit.

        As indicated, this method is meant to be reimplemented in subclasses.
        """
        self.pipe_closed.emit(await self.process.wait())

    def env(self) -> dict:
        """Returns the environment to use in the process.

        Reimplement in a subclas to change it.
        """
        return {
            # Copy parent's environment. SYSTEMROOT environment variable is required to
            # create network connections using getaddrinfo() (https://stackoverflow.com/a/14587915)
            **os.environ.copy(),
            # Set encoding of subprocess
            "PYTHONIOENCODING": "utf-8",
            # Use unbuffered pipe to enable streaming of program output to GUI
            "PYTHONUNBUFFERED": "1",
        }

    def stdout(self) -> int | IO[Any] | None:
        """Returns the pipe used by stdout of the process.

        Reimplement in a subclass to change it.
        """
        return None

    def stderr(self) -> int | IO[Any] | None:
        """Returns the pipe used by stderr of the process.

        Reimplement in a subclass to change it.
        """
        return None

    @override
    def run(self):
        try:
            self.__connectSignalToSlot()

            self._logger.debug(
                f"Starting process {self.pid}",
            )

            self._event_loop = qasync.QEventLoop(self)
            asyncio.set_event_loop(self._event_loop)
            asyncio.run(self._run())
        except Exception:
            self._logger.error(
                f"Process {self.pid} failed:\n{traceback.format_exc(limit=CoreArgs._core_traceback_limit)}",
                pid=self.pid,
            )
            # TODO: Figure out whether we should stop the thread manager on failure or continue with the remaining processes.
            #       (Maybe make it a config option??)
            #       Since nothing is done here, the thread manager keeps self.pid reserved for this process forever.

    @override
    def quit(self):
        """Stop the event loop, perform cleanup, and shut down.

        Equivalent to calling `self.exit(0)`.
        """
        self._terminate_process()
        self._event_loop.stop()
        return super().quit()

    @override
    def exit(self, returnCode: int):
        """Stop the event loop, perform cleanup, shut down, and exit with a return code."""
        self._terminate_process()
        self._event_loop.stop()
        return super().exit(returnCode)

    @override
    def terminate(self):
        """Terminates the execution of the thread.

        # Warning
        This function is dangerous and its use is discouraged.

        The thread can be terminated at any point in its code path.
        It can be terminated while modifying data. There is no chance
        for the thread to clean up after itself, unlock any held mutexes, etc.
        In short, use this function only if absolutely necessary.
        """
        self._kill_process()
        self._event_loop.stop()
        self._event_loop.close()
        return super().terminate()
