from abc import ABC, abstractmethod
import multiprocessing as mp
from xyztank.events import *


class View(ABC):
    """
    Abstract class of view.
    """

    def __init__(self, event_queue: mp.Queue):
        self.event_queue = event_queue

    def send_event(self, event: Event):
        """
        Sends event to the controller.
        """
        self.event_queue.put(event)

    def start(self):
        """
        Starts view.

        Note: this method uses the current thread to run main loop.
        """
        self.main_loop()

    @abstractmethod
    def main_loop(self):
        """
        Main loop of the window.
        """
        raise ValueError("Abstract method")

