import requests

from utils.patterns.producer_consumer import Producer
from utils.proxy.proxy import ProxyMng


class EncarProducer(Producer):

    def _init(self, *args, **kwargs):
        self.__url: str = kwargs.get("url")

    def run(self):
        pass

