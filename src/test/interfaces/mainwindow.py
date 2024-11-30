from qfluentwidgets import FluentIcon as FIF

from applib.app.interfaces.main_window import CoreMainWindow
from applib.app.interfaces.home_interface import CoreHomeInterface
from test.interfaces.process import TestProcessInterface
from test.interfaces.settings import TestSettingsInterface


class TestMainWindow(CoreMainWindow):
    def __init__(self):
        super().__init__(
            subinterfaces=[
                (CoreHomeInterface, FIF.HOME, "Home"),
                (TestProcessInterface, FIF.IOT, "Process"),
            ],
            settings_interface=(TestSettingsInterface, FIF.SETTING, "Settings"),
            app_icon=FIF.AIRPLANE.qicon(),
        )
