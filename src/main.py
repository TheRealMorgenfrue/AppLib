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


if __name__ == "__main__":
    from applib.app.core_app import CoreApp
    from applib.app.interfaces.main_window import CoreMainWindow

    app = CoreApp(CoreMainWindow)
