from abc import abstractmethod
from typing import List

from utils.patterns.mediator import Mediator
from utils.patterns.producer_consumer import Producer, Consumer
from utils.patterns.singleton import Singleton


class Manager(Mediator, metaclass=Singleton):
    _consumers: List[Consumer] = list()
    _producers: List[Producer]

    def __init__(self):
        if not self.__class__.is_instance():
            return
        super().__init__()
        self._consumers: List[Consumer] = list()
        self._producers: List[Producer] = list()
        self._init()

    @abstractmethod
    def _init(self):
        pass
