from datetime import datetime
import os
from pathlib import Path

from ...tools.version import VERSION


class CoreArgs:
    # ┌───────────────────┐
    # │ AppLib attributes │
    # └───────────────────┘
    # General
    _core_app_name = "AppLib"
    _core_app_version = VERSION
    _core_link_github = "https://github.com/TheRealMorgenfrue/AppLib"
    _core_is_release = False
    _core_traceback_limit = 0 if _core_is_release else None
    _core_app_dir = os.environ["APPLIB_PATH"]

    # Logging
    _core_log_dir = Path(_core_app_dir, "logs")
    _core_log_format = "%(asctime)s - %(module)s - %(lineno)s - %(levelname)s - %(message)s"  # %(asctime)s - %(name)s - %(levelname)s - %(message)s'
    _core_log_use_color = True
    _core_log_filename = datetime.now().strftime("%Y-%m-%d")
    _core_log_disable_header = False

    # Templates
    _core_main_template_name = _core_app_name
    _core_config_units = {}
    _core_template_loglevels = ["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"]
    _core_template_themes = ["Light", "Dark", "System"]

    # Configs
    _core_config_dir = Path(_core_app_dir, "configs")
    _core_main_config_name = _core_app_name
    _core_main_config_file = f"{_core_main_config_name}_config.toml"
    _core_main_config_path = str(Path(_core_config_dir, _core_main_config_file))

    # Asset directories
    _core_assets_dir = Path(_core_app_dir, "assets")
    _core_logo_dir = Path(_core_assets_dir, "logos")
    _core_icon_dir = Path(_core_assets_dir, "icons")  # Not used atm.
    _core_images_dir = Path(_core_assets_dir, "images")
    _core_qss_dir = Path(_core_assets_dir, "qss")

    # Asset paths
    _core_app_logo_path = str(Path(_core_logo_dir, "logo.png"))
