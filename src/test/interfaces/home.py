from applib.app.interfaces.home_interface import CoreHomeInterface
from test.modules.config.test_config import TestConfig


class TestHomeInterface(CoreHomeInterface):
    def __init__(self, parent=None):
        super().__init__(TestConfig(), parent)
