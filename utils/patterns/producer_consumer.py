import threading
from abc import abstractmethod, ABCMeta


class Consumer(threading.Thread, metaclass=ABCMeta):

    def __init__(self, *args, **kwargs):
        super(Consumer, self).__init__()
        self._init(*args, **kwargs)

    @abstractmethod
    def _init(self, *args, **kwargs): pass


class Producer(threading.Thread, metaclass=ABCMeta):

    def __init__(self, *args, **kwargs):
        super(Producer, self).__init__()
        self._init(*args, **kwargs)

    @abstractmethod
    def _init(self, *args, **kwargs): pass
