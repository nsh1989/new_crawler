from abc import abstractmethod
from enum import Enum, auto

from utils.patterns.mediator import Mediator
from utils.patterns.singleton import Singleton


# MngState: Enum = Enum('MngState', "START RUNNING DONE")
class MngState(Enum):
    START = auto()
    RUNNING = auto()
    DONE = auto()


class Manager(Mediator, metaclass=Singleton):

    def __init__(self, *args, **kwargs):
        if not self.__class__.is_instance():
            return
        super().__init__()
        self._init(*args, **kwargs)

    @abstractmethod
    def _init(self, *args, **kwargs):
        pass
