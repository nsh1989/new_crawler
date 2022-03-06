import threading

from utils.manager import Manager


class DatMng(Manager, threading.Thread):

    def _init(self):
        pass

    def execute(self):
        pass

    def notify(self, sender: object, event: str) -> None:
        pass

    def __init__(self, parnet: Manager):
        super().__init__()
        self.__parent = parnet
        self.__state = "START"