from applib.module.config.core_config import CoreConfig
from applib.module.config.internal.core_args import CoreArgs
from qfluentwidgets import FluentIcon as FIF

from applib.app.interfaces.main_window import CoreMainWindow
from test.interfaces.home import TestHomeInterface
from test.interfaces.process import TestProcessInterface
from test.interfaces.settings import TestSettingsInterface
from test.modules.config.test_args import TestArgs
from test.modules.config.test_config import TestConfig


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
