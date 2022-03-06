import random
import threading
from typing import List

from utils.manager import Manager, MngState
from utils.patterns.producer_consumer import Consumer, Producer


class CrawlerMng(Manager, threading.Thread):

    def _init(self, *args, **kwargs):
        self._consumers: List[Consumer] = list()
        self._producers: List[Producer] = list()
        self.__parent = kwargs.get("parent")
        self.__state: MngState = MngState.START

    @property
    def state(self):
        return self.__state

    def run(self):
        self.__state = MngState.RUNNING
        while True:
            test: int = random.randint(1, 10)
            self.__parent.notify(self, f"test event {test}")
            if test.__eq__(5):
                self.__state = MngState.DONE
                break

    def notify(self, sender: object, event: str) -> None:
        pass
