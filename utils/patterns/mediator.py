from abc import ABCMeta, abstractmethod, ABC


class Mediator(object):

    @abstractmethod
    def notify(self, sender: object, event: str) -> None: pass
