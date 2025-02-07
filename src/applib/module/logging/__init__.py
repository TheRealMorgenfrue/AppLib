import logging
import os
from pathlib import Path
from typing import Self, Union

from ..configuration.internal.core_args import CoreArgs
from .create_logger import create_logger


class AppLibLogger:
    _instance = None
    _loggers = []

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._created = False
        return cls._instance

    def __init__(self):
        if not self._created:
            self.logger = create_logger(
                name=CoreArgs._core_app_name,
                format=CoreArgs._core_log_format,
                log_dir=CoreArgs._core_log_dir,
                log_filename=CoreArgs._core_log_filename,
            )
            self._loggers.append(self.logger)
            self._created = True

    def writeHeaderToLog(self) -> None:
        if not CoreArgs._core_log_disable_header:
            self.logger_nocolor = create_logger(
                name=f"{CoreArgs._core_app_name}_nocolor",
                level="INFO",
                use_color=False,
                log_dir=CoreArgs._core_log_dir,
                log_filename=CoreArgs._core_log_filename,
            )
            self._loggers.append(self.logger_nocolor)

            padding = 90
            header = (
                "┌"
                + "─" * padding
                + "┐"
                + "\n"
                + "│"
                + f"Starting application".center(padding, " ")
                + "│"
                + "\n"
                + "└"
                + "─" * padding
                + "┘"
            )
            self.logger_nocolor.info(f"\n{header}")

    def setLogDir(self, logdir: Union[Path, str]) -> None:
        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                os.makedirs(logdir, exist_ok=True)
                handler.setStream(
                    open(
                        Path(logdir, f"{CoreArgs._core_log_filename}.log"),
                        "a",
                        encoding="utf-8",
                    )
                )

    def getAllLoggers(self) -> list[logging.Logger]:
        return self._loggers

    def getLogger(self) -> logging.Logger:
        """The main logger"""
        return self.logger
