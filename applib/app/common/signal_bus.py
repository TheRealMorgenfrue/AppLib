from PyQt6.QtCore import QObject, pyqtSignal


class SignalBus(QObject):
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
    # PixivUtil2
    # ───────────────────────────────────────────────────────────────────────────#

    # job_type: str, ids: str, save: bool
    # Notify process generator that Pixiv IDs are changed
    # Send the *job_type* along with the *ids* (needs parsing first)
    # Whether the process generator saves the parsed ids to config is determined by *save*
    pixivIDChanged = pyqtSignal(str, str, bool)

    # job_name: str, title: str, content: str, isSuccess: bool, save: bool
    # Notify that the Pixiv IDs have been loaded from input
    pixivIDsLoaded = pyqtSignal(str, str, str, bool, bool)

    # isRunning: bool
    # Notify whether PixivUtil2 is running in a ThreadManager
    isProcessesRunning = pyqtSignal(bool)

    # compatMode: int
    # 0 = None, 1 = Partial, 2 = Full
    enablePUCompatMode = pyqtSignal(int)


signalBus = SignalBus()
