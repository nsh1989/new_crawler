from abc import abstractmethod


class Mediator(object):

    @abstractmethod
    def notify(self, sender: object, event: str) -> None: pass
