import os
import sys
from pathlib import Path

from ...tools.version import VERSION


def getRuntimeMode() -> str:
    """Returns whether we are frozen via PyInstaller, Nuitka or similar
    This will affect how we find out where we are located.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # print("Running in a PyInstaller bundle")
        return "PYI"
    elif getattr(sys, "nuitka", False):
        # print("Running in a Nuitka onefile binary")
        return "NUI"
    # print("Running in a normal Python process")


def getAppPath() -> Path:
    """This will get us the program's directory,
    even if we are frozen using PyInstaller, Nuitka or similar"""
    mode = getRuntimeMode()
    if mode == "PYI":
        # The original path to the PyInstaller bundle
        return os.path.dirname(sys.argv[0])
    elif mode == "NUI":
        # The original path to the binary executable
        return os.path.dirname(sys.argv[0])
    # cwd must be set elsewhere. Preferably in the main '.py' file (e.g. app.py)
    return Path.cwd()


def getAssetsPath() -> Path:
    """This will get us the program's asset directory,
    even if we are frozen using PyInstaller, Nuitka or similar"""
    mode = getRuntimeMode()
    if mode == "PYI":
        # PyInstaller-specific way of getting path to extracted dir
        return Path(sys._MEIPASS).resolve()
    elif mode == "NUI":
        # The temporary or permanent path the bootstrap executable unpacks to (i.e. the temp data folder created by Nuitka onefile binaries at runtime)
        return Path.cwd()
    # cwd must be set elsewhere. Preferably in the main '.py' file (e.g. app.py)
    return Path.cwd()


class AppArgs:
    # General
    app_version = VERSION
    link_github = ""
    is_release = False
    traceback_limit = 0 if is_release else None
    app_dir = getAppPath()

    # Files
    app_toml = "app_config.toml"

    # Names
    app_name = "AppLib"
    app_template_name = app_name
    app_config_name = app_template_name

    # Logging
    log_dir = Path(app_dir, "logs")
    log_format = "%(asctime)s - %(module)s - %(lineno)s - %(levelname)s - %(message)s"  # %(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_format_color = "%(asctime)s - %(module)s - %(lineno)s - %(levelname)s - %(message)s"  # %(asctime)s - %(module)s - %(lineno)s - %(levelname)s - %(message)s'

    # Template Settings
    config_units = {
        # "second": "seconds",
        # "retry": "retries",
        # "tag": "tags",
        # "day": "days",
        # "kB": "",
    }

    # Configs
    config_dir = Path(app_dir, "configs")
    app_config_path = Path(config_dir, app_toml).resolve()

    # Assets
    assets_dir = Path(getAssetsPath(), "assets")
    logo_dir = Path(assets_dir, "logo")
    app_assets_dir = Path(assets_dir, "app")
    asset_icon_dir = Path(app_assets_dir, "icons")
    asset_images_dir = Path(app_assets_dir, "images")
    qss_dir = Path(app_assets_dir, "qss")

    # Template values - these are present to decouple several modules (logger, validators) from
    # the app template to prevent circular imports. NOT ideal, but a workaround for now
    template_loglevels = ["INFO", "WARN", "ERROR", "CRITICAL", "DEBUG"]
    template_themes = ["Light", "Dark", "System"]
