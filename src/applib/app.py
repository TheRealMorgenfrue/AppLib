# Nuitka Compilation mode
# nuitka-project: --onefile
# nuitka-project: --standalone
# nuitka-project: --include-data-dir={MAIN_DIRECTORY}/assets=assets

# Windows Controls
# nuitka-project: --windows-icon-from-ico={MAIN_DIRECTORY}/assets/logo/logo.png

# Binary Version Information
# nuitka-project: --product-name=APP_NAME
# nuitka-project: --product-version=0.0.0

# Plugin: Enable PyQt6 support and disable terminal for GUI application
# nuitka-project: --enable-plugin=PyQt6
# nuitka-project: --windows-console-mode=disable

# Plugin: Enable anti-bloat to remove dependency-heavy imports
# nuitka-project: --enable-plugin=anti-bloat


import os
import sys
from pathlib import Path

##########################
### Initial Path Setup ###
##########################
# Set initial CWD
os.chdir(os.path.dirname(os.path.abspath(__file__)))

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

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from app.main_window import MainWindow

# enable dpi scale
QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)

    try:
        from module.config.internal.app_args import AppArgs

        w = MainWindow()
        sys.exit(app.exec())
    except Exception:
        import traceback
        from datetime import datetime
        import time

        path = ""
        try:
            path = AppArgs.log_dir
        except Exception:
            path = Path.cwd()
        crashDir = Path(path, "crashes")
        os.makedirs(crashDir, exist_ok=True)

        line = "─" * 20
        header = f"{line} Crash reported at {time.asctime()} {line}\n"
        with open(
            Path(crashDir, f"crash {datetime.now().strftime("%Y-%m-%d")}.txt"),
            "a",
            encoding="utf-8",
        ) as file:
            file.write(f"{header}")
            file.write(traceback.format_exc())
            file.write("─" * len(header))
            file.write("\n\n")
