import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Self, Union


def createLogger(
    name: str,
    level: str = "DEBUG",
    format: str = "%(message)s",
    use_color: bool = True,
    log_dir: Union[Path, str, None] = None,
    log_filename: str = datetime.now().strftime("%Y-%m-%d"),
) -> logging.Logger:
    """
    Convenience function for creating a logger that follows AppLib's specification.

    Parameters
    ----------
    name : str
        The name of the logger.

    level : str, optional
        The initial log level.
        By default `"DEBUG"`.

    format : str, optional
        The format of log messages.

        Available format strings are:
            %(name)s
                Name of the logger (logging channel).
            %(levelno)s
                Numeric logging level for the message (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            %(levelname)s
                Text logging level for the message ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL").
            %(pathname)s
                Full pathname of the source file where the logging call was issued (if available).
            %(filename)s
                Filename portion of pathname.
            %(module)s
                Module (name portion of filename).
            %(lineno)d
                Source line number where the logging call was issued (if available).
            %(funcName)s
                Function name
            %(created)f
                Time when the LogRecord was created (time.time() return value).
            %(asctime)s
                Textual time when the LogRecord was created.
            %(msecs)d
                Millisecond portion of the creation time.
            %(relativeCreated)d
                Time in milliseconds when the LogRecord was created, relative to the time
                the logging module was loaded (typically at application startup time).
            %(thread)d
                Thread ID (if available).
            %(threadName)s
                Thread name (if available).
            %(taskName)s
                Task name (if available).
            %(process)d
                Process ID (if available).
            %(message)s
                The result of record.getMessage(), computed just as the record is emitted.

        By default `"%(message)s"`


    use_color : bool, optional
        Use color for level name `"%(levelname)s"`.
        Has no effect if level name is not used in `format`.
        By default `True`.

    log_dir : Union[Path, str, None], optional
        The directory for writing log files.
        If `None`, no log files will be created.
        By default `None`.

    log_filename : str, optional
        The name of the log file.
        Has no effect if `log_dir` is `None`.
        By default `datetime.now().strftime("%Y-%m-%d")`.

    Returns
    -------
    logging.Logger
        The created logger.
    """
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(level)

    if use_color:
        from .coloredformatter import ColoredFormatter
        from .colorcodefilter import ColorCodeFilter

        console_formatter = ColoredFormatter(format)
        file_formatter = ColorCodeFilter(format)
    else:
        console_formatter = logging.Formatter(format)
        file_formatter = logging.Formatter(format)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    if log_dir:
        if not Path(log_dir).exists():
            os.makedirs(log_dir)
        file_handler = logging.FileHandler(
            f"{log_dir}/{log_filename}.log",
            encoding="utf-8",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


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
            from ..config.internal.core_args import CoreArgs

            self.logger = createLogger(
                name=CoreArgs._core_app_name,
                format=CoreArgs._core_log_format,
                log_dir=CoreArgs._core_log_dir,
                log_filename=CoreArgs._core_log_filename,
            )
            self._loggers.append(self.logger)

            if not CoreArgs._core_log_disable_header:
                self.logger_nocolor = createLogger(
                    name=f"{CoreArgs._core_app_name}_nocolor",
                    level="INFO",
                    use_color=False,
                    log_dir=CoreArgs._core_log_dir,
                    log_filename=CoreArgs._core_log_filename,
                )
                self._writeHeaderToLog()
                self._loggers.append(self.logger_nocolor)
            self._created = True

    def _writeHeaderToLog(self) -> None:
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

    def getAllLoggers(self) -> list[logging.Logger]:
        return self._loggers

    def getLogger(self) -> logging.Logger:
        """The main logger"""
        return self.logger
