from interfaces.home import TestHomeInterface
from interfaces.process import TestProcessInterface
from interfaces.settings import TestSettingsInterface
from modules.config.test_args import TestArgs
from modules.config.test_config import TestConfig
from qfluentwidgets import FluentIcon as FIF

from applib.app.interfaces.main_window import CoreMainWindow


class TestMainWindow(CoreMainWindow):
    def __init__(self):
        super().__init__(
            MainArgs=TestArgs,
            MainConfig=TestConfig,
            subinterfaces=[
                (TestHomeInterface, FIF.HOME, "Home"),
                (TestProcessInterface, FIF.IOT, "Process"),
            ],
            settings_interface=(TestSettingsInterface, FIF.SETTING, "Settings"),
        )
