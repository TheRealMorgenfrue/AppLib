from applib.app.interfaces.home_interface import CoreHomeInterface
from applib.module.config.core_config import CoreConfig


class TestHomeInterface(CoreHomeInterface):
    def __init__(self, parent=None):
        super().__init__(CoreConfig(), parent)
