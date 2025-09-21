import os
import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget


class CoreApp:
    def __init__(self, MainWindow: type[QWidget]) -> None:
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
            print(f"{header}\n{content}\n{footer}")

            crash_dir = Path(Path.cwd(), "crashes")
            os.makedirs(crash_dir, exist_ok=True)
            with open(
                Path(
                    crash_dir,
                    f"crash {datetime.now().strftime("%Y-%m-%d")}.txt",
                ),
                "a",
                encoding="utf-8",
            ) as file:
                file.write(f"{header}\n{content}\n\n\n")
