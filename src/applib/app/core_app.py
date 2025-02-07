import os
import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget


class CoreApp:
    def __init__(self, MainWindow: QWidget) -> None:
        """
        The main class from which all other code is executed.

        NOTE: Only one instance of this class may be running.

        Parameters
        ----------
        MainWindow : QWidget
            A reference to the main window class of the GUI.
        """
        try:
            # Enable dpi scale
            QApplication.setHighDpiScaleFactorRoundingPolicy(
                Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
            )
            app = QApplication(sys.argv)
            app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)

            w = MainWindow()
            sys.exit(app.exec())
        except Exception:
            import time
            import traceback
            from datetime import datetime

            line = "─" * 20
            header = f"{line} Crash reported at {time.asctime()} {line}\n"
            content = traceback.format_exc()
            footer = "─" * len(header)
            terminal_str = f"{header}\n{content}\n{footer}"

            try:
                from ..module.logging import create_logger

                logger = create_logger("app_crash")
                logger.debug(terminal_str)
            except:  # Catch everything as we're crashing
                print(terminal_str)

            crash_dir = Path(Path.cwd(), "crashes")
            os.makedirs(crash_dir, exist_ok=True)
            with open(
                Path(
                    crash_dir,
                    f"crash {datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt",
                ),
                "a",
                encoding="utf-8",
            ) as file:
                file.write(header + "\n" + content)
