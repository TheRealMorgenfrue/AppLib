from datetime import datetime
from pathlib import Path


class TestArgs:
    # ┌─────────────────┐
    # │ Test attributes │
    # └─────────────────┘
    # General
    app_dir = Path().cwd()

    # Logging
    log_dir = Path(app_dir, "logs")
    log_format = "%(asctime)s - %(module)s - %(lineno)s - %(levelname)s - %(message)s"  # %(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_use_color = True
    log_filename = datetime.now().strftime("%Y-%m-%d")
    log_disable_header = True

    # Templates
    config_units = {
        "second": "seconds",
        "retry": "retries",
        "tag": "tags",
        "day": "days",
        "kB": "",
    }

    ## Main template
    main_template_name = "test_template"
    main_themes = ["Light", "Dark", "System"]

    ## Process template
    process_template_name = "process"

    # Configs
    config_dir = Path(app_dir, "configs")

    ## Main config
    main_config_name = "test_config"
    main_config_file = f"{main_config_name.replace(" ", "_").lower()}_config.toml"
    main_config_path = Path(config_dir, main_config_file)

    # ┌────────────────────────────┐
    # │ Override AppLib attributes │
    # └────────────────────────────┘
    # Logging
    _core_log_dir = log_dir
    _core_log_format = log_format
    _core_log_use_color = log_use_color
    _core_log_filename = log_filename
    _core_log_disable_header = False

    # Templates
    _core_main_template_name = main_template_name
    _core_config_units = config_units
    _core_template_themes = main_themes

    # Configs
    _core_config_dir = config_dir
    _core_main_config_name = main_config_name
    _core_main_config_file = main_config_file
    _core_main_config_path = main_config_path
