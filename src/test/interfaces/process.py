from PyQt6.QtWidgets import QWidget
from applib.app.interfaces.process.process_interface import CoreProcessInterface
from applib.module.concurrency.thread.thread_ui_streamer import ThreadUIStreamer
from applib.module.config.core_config import CoreConfig
from test.modules.concurrency.test_process_gen import TestProcessGenerator


class TestProcessInterface(CoreProcessInterface):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(CoreConfig(), TestProcessGenerator, ThreadUIStreamer, parent)
