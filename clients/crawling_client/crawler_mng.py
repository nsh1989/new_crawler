from utils.manager import Manager
from utils.patterns.producer_consumer import Consumer


class CrawlerMng(Manager):

    def _init(self):
        self._consumers.append(Consumer)

    def notify(self, sender: object, event: str) -> None:
        pass

    def get_size_consumers(self):
        return self._consumers
