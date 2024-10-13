from PyQt6.QtCore import QObject, pyqtSignal


class CoreSignalBus(QObject):
    # ───────────────────────────────────────────────────────────────────────────#
    # Config updates
    # ───────────────────────────────────────────────────────────────────────────#

    # isSuccess: bool, title: str, content: str
    # Notify whether a value was inserted in a config successfully or not
    configStateChange = pyqtSignal(bool, str, str)

    # config_name: str, configkey: str, value: tuple[Any]
    # Notify that a value in a config is updated
    # The tuple is a 1-tuple with the setting's value, e.g. (value,)
    configUpdated = pyqtSignal(str, str, tuple)

    # old_config_name: str, new_config_name: str
    configNameUpdated = pyqtSignal(str, str)

    # config_name: str
    # Force the config to be saved to disk
    doSaveConfig = pyqtSignal(str)

    # ───────────────────────────────────────────────────────────────────────────#
    # Setting updates
    # ───────────────────────────────────────────────────────────────────────────#

    # config_name: str, configkey: str, value: tuple[Any]
    # Update a setting's value programmatically from anywhere
    # The tuple is a 1-tuple with the setting's value, e.g. (value,)
    updateConfigSettings = pyqtSignal(str, str, tuple)

    # ───────────────────────────────────────────────────────────────────────────#
    # Errors
    # ───────────────────────────────────────────────────────────────────────────#

    # title: str, content: str
    # Notify the user that a generic program error has occurred
    genericError = pyqtSignal(str, str)

    # config_name: str, title: str, content: str
    # Notify the user that a config validation error occured
    configValidationError = pyqtSignal(str, str, str)

    # ───────────────────────────────────────────────────────────────────────────#
    # General
    # ───────────────────────────────────────────────────────────────────────────#

    # isRunning: bool
    # Notify whether processes are running in a ThreadManager
    isProcessesRunning = pyqtSignal(bool)


core_signalbus = CoreSignalBus()
