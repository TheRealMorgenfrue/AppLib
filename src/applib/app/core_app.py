import os
import sys
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget


class CoreApp:
    def __init__(self, MainWindow: QWidget) -> None:
        """
        The main class from which all other code is executed.

        Only one instance of this may be running.

        Parameters
        ----------
        MainWindow : QWidget
            A reference to the main window class of the GUI.
        """
        self.MainWindow = MainWindow
        self.setupPath()
        self.run()

    def setupPath(self) -> None:

        ##########################
        ### Initial Path Setup ###
        ##########################
        # Set initial CWD
        os.chdir(Path(os.path.abspath(__file__)).parents[3])

        # Running in a Nuitka onefile binary
        if Path(sys.argv[0]) != Path(__file__):
            setattr(sys, "nuitka", True)

        # # Running in a PyInstaller bundle
        # elif getattr(sys, "frozen", False):
        #     pass
        # # Running in a normal python process
        # else:
        #     pass
        ##########################

    def run(self) -> None:
        # enable dpi scale
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

        app = QApplication(sys.argv)
        app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)

        try:
            w = self.MainWindow()
            sys.exit(app.exec())
        except Exception:
            import traceback
            from datetime import datetime
            import time

            crashDir = Path(Path.cwd(), "crashes")
            os.makedirs(crashDir, exist_ok=True)

            line = "─" * 20
            header = f"{line} Crash reported at {time.asctime()} {line}\n"
            content = traceback.format_exc()
            footer = "─" * len(header)
            print(f"{header}\n{content}\n{footer}")  # For debugging
            with open(
                Path(crashDir, f"crash {datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt"),
                "a",
                encoding="utf-8",
            ) as file:
                file.write(header + "\n" + content)
