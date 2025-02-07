import asyncio
import os
import subprocess
import sys
from pathlib import Path

from applib.module.concurrency.process.process_base import ProcessBase
from applib.module.concurrency.process.stream_reader import async_read_pipe


class TestProcess(ProcessBase):
    def __init__(self) -> None:
        super().__init__()

    async def _run(self) -> None:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        env = {
            **os.environ.copy(),  # Copy parent's environment. SYSTEMROOT environment variable is required to create network connections using getaddrinfo() (https://stackoverflow.com/a/14587915)
            "PYTHONIOENCODING": "utf-8",  # Set encoding of subprocess
            "PYTHONUNBUFFERED": "1",  # Disable default buffering of subprocess
        }

        exe = (
            sys.executable,
            f"{Path(r"src\test\modules\concurrency\test_file_program.py").resolve()}",
        )
        args = ["--test"]
        self.process = await asyncio.create_subprocess_exec(
            *exe,
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            startupinfo=startupinfo,
            env=env,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )

        self._logger.debug(f"Process {self.process_id} started")
        await async_read_pipe(self.process, self.consoleStream)  # Thread Blocking
        self._logger.debug(f"Process {self.process_id} exited")
