from abc import ABC, abstractmethod
import multiprocessing as mp
from xyztank.events import *


class View(ABC):

    def __init__(self, event_queue: mp.Queue):
        self.event_queue = event_queue

    def send_event(self, event: Event):
        self.event_queue.put(event)

    def start(self):
        """
        Starts view.

        Note: this method uses the current thread to run main loop.
        """
        self.main_loop()

    @abstractmethod
    def main_loop(self):
        raise ValueError("Abstract method")

