import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Self, Union

from ..configuration.internal.core_args import CoreArgs

# Logger names for lookup
APPLIB_LOGGER_NAME = CoreArgs._core_app_name
APPLIB_LOGGER_NOCOLOR_NAME = f"{APPLIB_LOGGER_NAME}_nocolor"


class LoggingManager:
    _instance = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._created = False
        return cls._instance

    def __init__(self) -> None:
        if not self._created:
            self.loggers = {}
            self._created = True

    def applib_logger(self) -> logging.Logger:
        """Get the library logger"""
        return self.loggers[APPLIB_LOGGER_NAME]

    def set_log_dir(self, logger_name: str, log_dir: Union[Path, str]):
        """
        Update the directory of all handlers attached to the logger with
        name `logger_name`.

        Parameters
        ----------
        logger_name : str
            The name of the logger.
        log_dir : Union[Path, str]
            Set the logger's directory to this directory.
        """
        for handler in self.get_logger(logger_name).handlers:
            if isinstance(handler, logging.FileHandler):
                os.makedirs(log_dir, exist_ok=True)
                handler.setStream(
                    open(
                        Path(log_dir, f"{CoreArgs._core_log_filename}.log"),
                        "a",
                        encoding="utf-8",
                    )
                )

    def register_logger(self, logger: logging.Logger):
        """Register a custom logger to be managed by AppLib"""
        self.loggers[logger.name] = logger

    def get_logger(self, logger_name: str) -> logging.Logger:
        """Get a logger by its name"""
        return self.loggers[logger_name]  # KeyError if name is not present

    def delete_logger(self, logger_name: str):
        """Delete a logger by its name"""
        self.loggers.pop(logger_name, None)

    def create_logger(
        self,
        name: str,
        level: str = "DEBUG",
        format: str = "%(message)s",
        use_color: bool = True,
        log_dir: Union[Path, str, None] = None,
        log_filename: str = datetime.now().strftime("%Y-%m-%d"),
    ) -> logging.Logger:
        """
        Convenience function for creating a logger that follows AppLib's specification.
        The logger is automatically registered by the manager, so there's no need to call
        the `register_logger()` method.

        Parameters
        ----------
        name : str
            The name of the logger.

        level : str, optional
            The initial log level.
            By default "DEBUG".

        format : str, optional
            The format of log messages.

            Available format strings are:
                - %(name)s
                    Name of the logger (logging channel).
                - %(levelno)s
                    Numeric logging level for the message (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                - %(levelname)s
                    Text logging level for the message ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL").
                - %(pathname)s
                    Full pathname of the source file where the logging call was issued (if available).
                - %(filename)s
                    Filename portion of pathname.
                - %(module)s
                    Module (name portion of filename).
                - %(lineno)d
                    Source line number where the logging call was issued (if available).
                - %(funcName)s
                    Function name
                - %(created)f
                    Time when the LogRecord was created (time.time() return value).
                - %(asctime)s
                    Textual time when the LogRecord was created.
                - %(msecs)d
                    Millisecond portion of the creation time.
                - %(relativeCreated)d
                    Time in milliseconds when the LogRecord was created, relative to the time
                    the logging module was loaded (typically at application startup time).
                - %(thread)d
                    Thread ID (if available).
                - %(threadName)s
                    Thread name (if available).
                - %(taskName)s
                    Task name (if available).
                - %(process)d
                    Process ID (if available).
                - %(message)s
                    The result of record.getMessage(), computed just as the record is emitted.

            By default "%(message)s"


        use_color : bool, optional
            Use color for levelname.
            Has no effect if levelname is not used in `format`.
            By default True.

        log_dir : Union[Path, str, None], optional
            The directory for writing log files.
            If None, no log files will be created.
            By default None.

        log_filename : str, optional
            The name of the log file.
            Has no effect if `log_dir` is None.
            By default datetime.now().strftime("%Y-%m-%d").

        Returns
        -------
        logging.Logger
            The created logger.
        """
        logger = logging.getLogger(name)
        logger.propagate = False
        logger.setLevel(level)

        if use_color:
            from .colorcodefilter import ColorCodeFilter
            from .coloredformatter import ColoredFormatter

            console_formatter = ColoredFormatter(format)
            file_formatter = ColorCodeFilter(format)
        else:
            console_formatter = logging.Formatter(format)
            file_formatter = logging.Formatter(format)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        self.register_logger(logger)

        if log_dir:
            file_handler = logging.FileHandler(
                f"{log_dir}/{log_filename}.log", encoding="utf-8", delay=True
            )
            file_handler.setStream
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            self.set_log_dir(name, log_dir)

        return logger
