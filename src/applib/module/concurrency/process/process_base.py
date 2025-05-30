import asyncio
import time
import traceback
from abc import abstractmethod

from PyQt6.QtCore import QObject, pyqtSignal

from ...configuration.internal.core_args import CoreArgs
from ...logging import LoggingManager


# Signals must not be connected to slots in __init__
# as that will result in them being bound to the main thread
# (a good idea would be to connect signals in the "start" method instead)
class ProcessBase(QObject):
    finished = pyqtSignal(int)  # process_id
    failed = pyqtSignal(int)  # process_id
    consoleStream = pyqtSignal(str)  # Receives text (stdout+stderr) from subprocess

    def __init__(self) -> None:
        super().__init__()
        self._logger = LoggingManager().applib_logger()
        self.process = None  # type: asyncio.subprocess.Process
        self.process_id = None  # type: int

    def _cleanup(self, failed: bool = False) -> None:
        if failed:
            self.failed.emit(self.process_id)
        else:
            self.finished.emit(self.process_id)
        self.deleteLater()

    @abstractmethod
    async def _run(self) -> None: ...

    def terminate(self, timeout: float = 2.0) -> None:
        try:
            if self.process:
                self.process.terminate()
                time.sleep(timeout)
                if self.process.returncode is None:
                    raise TimeoutError()
        except ProcessLookupError:
            self._logger.debug(f"Process {self.process_id} is already dead")
        except TimeoutError:
            self._logger.warning(
                f"Process {self.process_id} exceeded its shutdown period. It will be killed forcefully"
            )
            self.process.kill()
        except Exception:
            self._logger.critical(
                f"Process {self.process_id} failed to commit suicide\n"
                + traceback.format_exc(limit=CoreArgs._core_traceback_limit)
            )
        finally:
            del self.process
            self.process = None

    def start(self) -> None:
        failed = False
        try:
            self.consoleStream.emit(f"Process started")
            # TODO: Enhance asyncio eventloops: https://github.com/MagicStack/uvloop
            asyncio.run(self._run())
        except Exception:
            failed = True
            err_msg = f"Process {self.process_id} failed\n" + traceback.format_exc(
                limit=CoreArgs._core_traceback_limit
            )
            self.consoleStream.emit(err_msg)
            self._logger.error(err_msg)
            self.terminate()
        finally:
            self._cleanup(failed)
