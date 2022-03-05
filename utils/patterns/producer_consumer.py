import threading
from abc import abstractmethod, ABCMeta


class Consumer(threading.Thread, metaclass=ABCMeta):

    def __init__(self):
        super(Consumer, self).__init__()

    @abstractmethod
    def execute(self): pass


class Producer(threading.Thread, metaclass=ABCMeta):

    def __init__(self):
        super(Producer, self).__init__()

    @abstractmethod
    def execute(self): pass
