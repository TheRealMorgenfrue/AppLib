from abc import abstractmethod
import asyncio
import time
import traceback

from PyQt6.QtCore import pyqtSignal, QObject

from module.config.internal.app_args import AppArgs
from module.logger import logger


# Signals must not be connected to slots in __init__
# as that will result in them being bound to the main thread
# (a good idea would be to connect signals in the "start" method instead)
class ProcessBase(QObject):
    _logger = logger
    finished = pyqtSignal(int)  # processID
    failed = pyqtSignal(int)  # processID
    consoleStream = pyqtSignal(str)  # Receives text (stdout+stderr) from subprocess

    def __init__(self) -> None:
        super().__init__()
        self.process = None  # type: asyncio.subprocess.Process
        self.processID = None  # type: int

    def _cleanup(self, failed: bool = False) -> None:
        if failed:
            self.failed.emit(self.processID)
        else:
            self.finished.emit(self.processID)
        self.deleteLater()

    @abstractmethod
    async def _run(self) -> None: ...

    def setProcessID(self, processID: int) -> None:
        self.processID = processID

    def getProcessID(self) -> int:
        return self.processID

    def terminate(self, timeout: float = 2.0) -> None:
        try:
            if self.process:
                self.process.terminate()
                time.sleep(timeout)
                if self.process.returncode is None:
                    raise TimeoutError()
        except ProcessLookupError:
            self._logger.debug(f"Process {self.processID} is already dead")
        except TimeoutError:
            self._logger.warning(
                f"Process {self.processID} exceeded its shutdown period. It will be killed forcefully"
            )
            self.process.kill()
        except Exception:
            self._logger.critical(
                f"Process {self.processID} failed to commit suicide\n"
                + traceback.format_exc(limit=AppArgs.traceback_limit)
            )
        finally:
            del self.process
            self.process = None

    def start(self) -> None:
        failed = False
        try:
            # Save reference to the event loop to allow coroutines to be
            # submitted to it outside of asyncio.run()
            self.consoleStream.emit(f"Process started")
            asyncio.run(self._run())
        except Exception:
            failed = True
            err_msg = f"Process {self.processID} failed\n" + traceback.format_exc(
                limit=AppArgs.traceback_limit
            )
            self.consoleStream.emit(err_msg)
            self._logger.error(err_msg)
            self.terminate()
        finally:
            self._cleanup(failed)
