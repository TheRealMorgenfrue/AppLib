from PyQt6.QtWidgets import QWidget
from applib.app.interfaces.process.process_interface import CoreProcessInterface
from applib.module.concurrency.thread.thread_ui_streamer import ThreadUIStreamer
from test.modules.concurrency.test_process_gen import TestProcessGenerator


class TestProcessInterface(CoreProcessInterface):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(TestProcessGenerator, ThreadUIStreamer, parent)