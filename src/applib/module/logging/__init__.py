import logging
import os
import re
from collections.abc import Callable
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Self

from PyQt6.QtCore import Qt, pyqtBoundSignal

from ..configuration.internal.core_args import CoreArgs

# Logger names for lookup. They must be placed here to prevent the name from being overridden
APPLIB_LOGGER_NAME = CoreArgs._core_app_name
APPLIB_LOGGER_NOCOLOR_NAME = f"{APPLIB_LOGGER_NAME}_nocolor"


class LoggingManager:
    class LogLevel(Enum):
        CRITICAL = 50
        ERROR = 40
        WARNING = 30
        INFO = 20
        DEBUG = 10

    _instance = None
    _loggers = {}
    _level = LogLevel.DEBUG

    _gui_msg_cache = []  # type: list[Callable]
    _proc_msg_cache = []  # type: list[Callable]
    _gui_msg_signal = None  # type: pyqtBoundSignal
    _proc_msg_signal = None  # type: pyqtBoundSignal

    _gui_ready = False
    """True if the GUI is ready to receive messages"""

    _proc_ready = False
    """True if the process interface is ready to receive messages"""

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _get_gui_orient(self, msg: str):
        return Qt.Orientation.Horizontal if len(msg) < 50 else Qt.Orientation.Vertical

    def _process_text_for_gui(self, text: str):
        return re.sub(pattern="\n", repl="<br>", string=text)

    def set_proc_signal(self, signal: pyqtBoundSignal):
        self._proc_msg_signal = signal

    def set_gui_signal(self, signal: pyqtBoundSignal):
        self._gui_msg_signal = signal

    def set_gui_ready(self, is_ready):
        self._gui_ready = is_ready
        if is_ready:
            for fn in self._gui_msg_cache:
                fn()
            self._gui_msg_cache = []

    def set_proc_ready(self, is_ready):
        self._proc_ready = is_ready
        if is_ready:
            for fn in self._proc_msg_cache:
                fn()
            self._proc_msg_cache = []

    def set_level(self, level: LogLevel | int | str):
        error = False
        if isinstance(level, LoggingManager.LogLevel):
            self._level = level
        elif isinstance(level, int):
            for enum in LoggingManager.LogLevel._member_map_.values():
                if enum.value == level:
                    self._level = enum
            else:
                error = True
        elif isinstance(level, str):
            for name in LoggingManager.LogLevel._member_names_:
                if level.lower() == name.lower():
                    self._level = LoggingManager.LogLevel._member_map_[name]
            else:
                error = True
        else:
            error = True

        if error:
            self.error(
                f"Invalid loglevel '{level}'. Expected a value in Enum '{LoggingManager.LogLevel.__name__}'"
            )
        else:
            self.applib_logger().setLevel(self._level.name)

    def debug(
        self,
        msg: Any,
        title: Any | None = None,
        log: bool = True,
        gui: bool = False,
        pid: int | None = None,
    ):
        """
        Convenience method for logging `msg` with loglevel DEBUG.

        Parameters
        ----------
        msg : Any
            The message to be logged.
        title: Any, optional
            The title of `msg`.
            NOTE: Only used by `gui`.
        log : bool, optional
            Log `msg` using the applib logger. By default True.
        gui : bool, optional
            Show `msg` in the GUI. By default False.
        pid : int | None, optional
            Write `msg` in the console window of process id `pid`. By default None.
        """
        if self._level.value <= LoggingManager.LogLevel.DEBUG.value:
            if not isinstance(msg, str):
                msg = f"{msg}"

            level = "debug"
            if log:
                self.applib_logger().debug(msg, stacklevel=2)
            if gui:
                if title is None:
                    title = "Debug"
                elif not isinstance(title, str):
                    title = f"{title}"

                if self._gui_ready:
                    self._gui_msg_signal.emit(
                        level,
                        self._process_text_for_gui(title),
                        self._process_text_for_gui(msg),
                        self._get_gui_orient(msg),
                    )
                else:
                    func = lambda msg=msg, title=title, log=False, gui=gui, pid=None: self.debug(
                        msg=msg, title=title, log=log, gui=gui, pid=pid
                    )
                    self._gui_msg_cache.append(func)
            if pid is not None:
                if self._proc_msg_signal is not None:
                    if self._proc_ready:
                        self._proc_msg_signal.emit(level, pid, msg)
                    else:
                        func = (
                            lambda msg=msg, log=False, gui=False, pid=pid: self.debug(
                                msg=msg, log=log, gui=gui, pid=pid
                            )
                        )
                        self._proc_msg_cache.append(func)
                else:
                    self.applib_logger().warning(
                        f"Cannot send process signal: signal is {self._proc_msg_signal}"
                    )

    def info(
        self,
        msg: Any,
        title: Any | None = None,
        log: bool = True,
        gui: bool = False,
        pid: int | None = None,
    ):
        """
        Convenience method for logging `msg` with loglevel INFO.

        Parameters
        ----------
        msg : Any
            The message to be logged.
        title: Any | None, optional
            The title of `msg`.
            NOTE: Only used by `gui`.
        log : bool, optional
            Log `msg` using the applib logger. By default True.
        gui : bool, optional
            Show `msg` in the GUI. By default False.
        pid : int | None, optional
            Write `msg` in the console window of process id `pid`. By default None.
        """
        if self._level.value <= LoggingManager.LogLevel.INFO.value:
            if not isinstance(msg, str):
                msg = f"{msg}"

            level = "info"
            if log:
                self.applib_logger().info(msg, stacklevel=2)
            if gui:
                if title is None:
                    title = "Info"
                elif not isinstance(title, str):
                    title = f"{title}"

                if self._gui_ready:
                    self._gui_msg_signal.emit(
                        level,
                        self._process_text_for_gui(title),
                        self._process_text_for_gui(msg),
                        self._get_gui_orient(msg),
                    )
                else:
                    func = lambda msg=msg, title=title, log=False, gui=gui, pid=None: self.info(
                        msg=msg, title=title, log=log, gui=gui, pid=pid
                    )
                    self._gui_msg_cache.append(func)
            if pid is not None:
                if self._proc_msg_signal is not None:
                    if self._proc_ready:
                        self._proc_msg_signal.emit(level, pid, msg)
                    else:
                        func = lambda msg=msg, log=False, gui=False, pid=pid: self.info(
                            msg=msg, log=log, gui=gui, pid=pid
                        )
                        self._proc_msg_cache.append(func)
                else:
                    self.applib_logger().warning(
                        f"Cannot send process signal: signal is {self._proc_msg_signal}"
                    )

    def warning(
        self,
        msg: Any,
        title: Any | None = None,
        log: bool = True,
        gui: bool = False,
        pid: int | None = None,
    ):
        """
        Convenience method for logging `msg` with loglevel WARNING.

        Parameters
        ----------
        msg : Any
            The message to be logged.
        title: Any, optional
            The title of `msg`.
            NOTE: Only used by `gui`.
        log : bool, optional
            Log `msg` using the applib logger. By default True.
        gui : bool, optional
            Show `msg` in the GUI. By default False.
        pid : int | None, optional
            Write `msg` in the console window of process id `pid`. By default None.
        """
        if self._level.value <= LoggingManager.LogLevel.WARNING.value:
            if not isinstance(msg, str):
                msg = f"{msg}"

            level = "warning"
            if log:
                self.applib_logger().warning(msg, stacklevel=2)
            if gui:
                if title is None:
                    title = "Warning"
                elif not isinstance(title, str):
                    title = f"{title}"

                if self._gui_ready:
                    self._gui_msg_signal.emit(
                        level,
                        self._process_text_for_gui(title),
                        self._process_text_for_gui(msg),
                        self._get_gui_orient(msg),
                    )
                else:
                    func = lambda msg=msg, title=title, log=False, gui=gui, pid=None: self.warning(
                        msg=msg, title=title, log=log, gui=gui, pid=pid
                    )
                    self._gui_msg_cache.append(func)
            if pid is not None:
                if self._proc_msg_signal is not None:
                    if self._proc_ready:
                        self._proc_msg_signal.emit(level, pid, msg)
                    else:
                        func = (
                            lambda msg=msg, log=False, gui=False, pid=pid: self.warning(
                                msg=msg, log=log, gui=gui, pid=pid
                            )
                        )
                        self._proc_msg_cache.append(func)
                else:
                    self.applib_logger().warning(
                        f"Cannot send process signal: signal is {self._proc_msg_signal}"
                    )

    def error(
        self,
        msg: Any,
        title: Any | None = None,
        log: bool = True,
        gui: bool = False,
        pid: int | None = None,
    ):
        """
        Convenience method for logging `msg` with loglevel ERROR.

        Parameters
        ----------
        msg : Any
            The message to be logged.
        title: Any | None, optional
            The title of `msg`.
            NOTE: Only used by `gui`.
        log : bool, optional
            Log `msg` using the applib logger. By default True.
        gui : bool, optional
            Show `msg` in the GUI. By default False.
        pid : int | None, optional
            Write `msg` in the console window of process id `pid`. By default None.
        """
        if self._level.value <= LoggingManager.LogLevel.ERROR.value:
            if not isinstance(msg, str):
                msg = f"{msg}"

            level = "error"
            if log:
                self.applib_logger().error(msg, stacklevel=2)
            if gui:
                if title is None:
                    title = "Error"
                elif not isinstance(title, str):
                    title = f"{title}"

                if self._gui_ready:
                    self._gui_msg_signal.emit(
                        level,
                        self._process_text_for_gui(title),
                        self._process_text_for_gui(msg),
                        self._get_gui_orient(msg),
                    )
                else:
                    func = lambda msg=msg, title=title, log=False, gui=gui, pid=None: self.error(
                        msg=msg, title=title, log=log, gui=gui, pid=pid
                    )
                    self._gui_msg_cache.append(func)
            if pid is not None:
                if self._proc_msg_signal is not None:
                    if self._proc_ready:
                        self._proc_msg_signal.emit(level, pid, msg)
                    else:
                        func = lambda msg=msg, log=False, gui=False, pid=pid: self.info(
                            msg=msg, log=log, gui=gui, pid=pid
                        )
                        self._proc_msg_cache.append(func)
                else:
                    self.applib_logger().warning(
                        f"Cannot send process signal: signal is {self._proc_msg_signal}"
                    )

    def critical(
        self,
        msg: Any,
        title: Any | None = None,
        log: bool = True,
        gui: bool = False,
        pid: int | None = None,
    ):
        """
        Convenience method for logging `msg` with loglevel CRITICAL.

        Parameters
        ----------
        msg : Any
            The message to be logged.
        title: Any, optional
            The title of `msg`.
            NOTE: Only used by `gui`.
        log : bool, optional
            Log `msg` using the applib logger. By default True.
        gui : bool, optional
            Show `msg` in the GUI. By default False.
        pid : int | None, optional
            Write `msg` in the console window of process id `pid`. By default None.
        """
        if self._level.value <= LoggingManager.LogLevel.CRITICAL.value:
            if not isinstance(msg, str):
                msg = f"{msg}"

            level = "critical"
            if log:
                self.applib_logger().critical(msg, stacklevel=2)
            if gui:
                if title is None:
                    title = "Critical Error"
                elif not isinstance(title, str):
                    title = f"{title}"

                if self._gui_ready:
                    self._gui_msg_signal.emit(
                        level,
                        self._process_text_for_gui(title),
                        self._process_text_for_gui(msg),
                        self._get_gui_orient(msg),
                    )
                else:
                    func = lambda msg=msg, title=title, log=False, gui=gui, pid=None: self.critical(
                        msg=msg, title=title, log=log, gui=gui, pid=pid
                    )
                    self._gui_msg_cache.append(func)
            if pid is not None:
                if self._proc_msg_signal is not None:
                    if self._proc_ready:
                        self._proc_msg_signal.emit(level, pid, msg)
                    else:
                        func = lambda msg=msg, log=False, gui=False, pid=pid: self.critical(
                            msg=msg, log=log, gui=gui, pid=pid
                        )
                        self._proc_msg_cache.append(func)
                else:
                    self.applib_logger().warning(
                        f"Cannot send process signal: signal is {self._proc_msg_signal}"
                    )

    def applib_logger(self) -> logging.Logger:
        """Get the library logger"""
        return self._loggers[APPLIB_LOGGER_NAME]

    def set_log_dir(self, logger_name: str, log_dir: Path | str):
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
        self._loggers[logger.name] = logger

    def get_logger(self, logger_name: str) -> logging.Logger:
        """Get a logger by its name"""
        return self._loggers[logger_name]  # KeyError if name is not present

    def delete_logger(self, logger_name: str):
        """Delete a logger by its name"""
        self._loggers.pop(logger_name, None)

    def create_logger(
        self,
        name: str,
        level: str = "DEBUG",
        format: str = "%(message)s",
        use_color: bool = True,
        log_dir: Path | str | None = None,
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
