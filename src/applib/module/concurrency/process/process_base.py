import traceback

from PyQt6.QtCore import (
    QObject,
    QProcess,
    QProcessEnvironment,
    QStringDecoder,
    pyqtSignal,
)

from ...configuration.internal.core_args import CoreArgs
from ...logging import LoggingManager


# Signals must not be connected to slots in __init__
# as that will result in them being bound to the main thread
# (a good idea would be to connect signals in the "start" method instead)
class ProcessBase(QObject):
    finished = pyqtSignal(int)
    """The process finished successfully.

    Parameters
    ----------
    process_id : int
        The id of the process.
    """

    failed = pyqtSignal(int)
    """The process failed in some way.

    Parameters
    ----------
    process_id : int
        The id of the process.
    """

    kill = pyqtSignal()
    """Kill the process immediately."""

    terminate = pyqtSignal()
    """Terminate process."""

    start = pyqtSignal()
    """Start process."""

    def __init__(self):
        """The base class for processes.

        NOTE: All communication with the process should be made using the signal/slot system.
        """
        super().__init__()
        self._logger = LoggingManager()
        self._initialized = False
        self.process = None  # type: QProcess
        self.process_environment = None  # type: QProcessEnvironment
        self.process_id = None  # type: int
        self.program = ""
        self.args = []
        self.decoder = None  # type: QStringDecoder

        self._killed = False
        self._terminated = False

    def __connectSignalToSlot(self):
        self.process.errorOccurred.connect(self._onProcessError)
        self.process.finished.connect(self._onProcessFinished)
        self.process.readyReadStandardOutput.connect(self._onReadyStdOut)
        self.process.readyReadStandardError.connect(self._onReadyStdErr)
        self.kill.connect(self._killProcess)
        self.terminate.connect(self._terminate)
        self.start.connect(self._start)

    def _onReadyStdOut(self):
        self.process.setReadChannel(QProcess.ProcessChannel.StandardOutput)
        self._logger.info(
            self.decoder.decode(self.process.readLine()),
            log=False,
            pid=self.process_id,
        )

    def _onReadyStdErr(self):
        self.process.setReadChannel(QProcess.ProcessChannel.StandardError)
        self._logger.error(
            self.decoder.decode(self.process.readLine()), log=False, pid=self.process_id
        )

    def _onProcessError(self, code: int):
        match code:
            # The process failed to start
            case QProcess.ProcessError.FailedToStart:
                self._logger.error(
                    f"Process {self.process_id} failed to start", pid=self.process_id
                )
            # The process crashed some time after starting successfully
            case QProcess.ProcessError.Crashed:
                if self._killed:
                    return
                self._logger.error(
                    f"Process {self.process_id} crashed", pid=self.process_id
                )
            # The last waitFor...() function timed out
            case QProcess.ProcessError.Timedout:
                self._logger.info(
                    f"Process {self.process_id} timed out while terminating and will be killed forcefully",
                    pid=self.process_id,
                )
                self.process.kill()
            # An error occurred when attempting to read from the process
            case QProcess.ProcessError.ReadError:
                self._logger.error(
                    f"Failed to read from process {self.process_id}",
                    pid=self.process_id,
                )
                self._terminate()
            # An error occurred when attempting to write to the process
            case QProcess.ProcessError.WriteError:
                self._logger.error(
                    f"Failed to write to process {self.process_id}", pid=self.process_id
                )
                self._terminate()
            # An unknown error occurred
            case QProcess.ProcessError.UnknownError:
                self._logger.error(
                    f"Process {self.process_id} encountered an unknown error",
                    pid=self.process_id,
                )
                self._terminate()
            # The error codes have been extended but is not supported here
            case _:
                self._logger.warning(
                    f"Unsupported error code {code} created by process {self.process_id}",
                    pid=self.process_id,
                )
                self._terminate()

    def _onProcessFinished(self, exitCode: int, exitStatus: QProcess.ExitStatus):
        """
        Determine if a finished process is considered to have failed or not.

        A failed process will be treated as if it had not been run.
        Thus, its arguments will be rescheduled by the thread manager.

        Parameters
        ----------
        exitCode : int
            The exit code of the process.
        exitStatus : QProcess.ExitStatus
            The exit status of the process.
        """
        if not (self._killed or self._terminated):
            if exitCode == 0:
                self.finished.emit(self.process_id)
            else:
                self._logger.error(
                    f"Process exited with error code {exitCode}", pid=self.process_id
                )
                # TODO: Temporary until process failure is handled properly in thread_manager
                # When that happens, move it outside of if-statement
                self.failed.emit(self.process_id)

    def _killProcess(self):
        self._logger.info(f"Killing process {self.process_id}")
        self._killed = True
        self.process.kill()

    def _terminate(self):
        self._logger.info(f"Terminating process {self.process_id}")
        self._terminated = True
        self.process.terminate()
        self.process.waitForFinished(10000)

    def _setup(self):
        environ = QProcessEnvironment(
            QProcessEnvironment.Initialization.InheritFromParent
        )
        # Set encoding of subprocess
        environ.insert("PYTHONIOENCODING", "utf-8")
        # Disable default buffering of subprocess
        environ.insert("PYTHONUNBUFFERED", "1")

        self.process = QProcess(self)
        self.process.setProcessEnvironment(environ)
        self.decoder = QStringDecoder(QStringDecoder.Encoding.Utf8)
        self.__connectSignalToSlot()
        self._initialized = True

    def setProgram(self, program: str):
        self.program = program

    def setArguments(self, args: list[str]):
        self.args = args

    def _start(self):
        self._terminated = False
        self._killed = False
        try:
            if not self._initialized:
                self._setup()

            self._logger.info(
                f"Starting process",
                log=True,
                gui=False,
                pid=self.process_id,
            )
            self.process.start(self.program, self.args)
        except Exception:
            self._logger.error(
                f"Failed to start process {self.process_id}\n{traceback.format_exc(limit=CoreArgs._core_traceback_limit)}",
                pid=self.process_id,
            )
            self._terminate()
