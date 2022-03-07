import queue
import random
import threading
import trace
from queue import Queue
from typing import List

import requests
from requests import Response

from clients.crawling_client.encar_producer import EncarProducer
from utils import Configs
from utils.manager import Manager, MngState
from utils.patterns.producer_consumer import Consumer, Producer
from utils.proxy.proxy import ProxyMng


class CrawlerMng(Manager, threading.Thread):
    __state: MngState
    __producerNum: int = 5
    __consumerNum: int = 5

    def _init(self, *args, **kwargs):
        self._consumers: List[Consumer] = list()
        self._producers: List[Producer] = list()
        self.__producerTaskQue: Queue = Queue()
        self.__proxyMng: ProxyMng = ProxyMng()
        self.__parent = kwargs.get("parent")
        self.__state = MngState.START

    @property
    def state(self):
        return self.__state

    def __set_producer_task_que(self):
        s: requests.session = requests.session()
        s.headers.update(Configs.headers[0])
        params = {
            'count': 'ture',
            'q': '(And.Hidden.N._.CarType.N._.Condition.Inspection._.Condition.Record.)',
            'sr': '|ModifiedDate|0|100'
        }
        resp: Response = Response()
        url = 'http://api.encar.com/search/car/list/premium'
        try:
            resp = s.get(url, params=params)
        except requests.exceptions as e:
            trace.Trace(e)
            raise e
        if resp.status_code != 200:
            raise Exception("Something is Wrong encar_producer __get_total_pages")
        total_pages: int = round(resp.json()['Count'] / 100)
        [self.__producerTaskQue.put(i) for i in range(0, total_pages)]

    def __set_producers_consumers(self):
        for i in range(0, self.__producerNum):
            self._producers.append(Producer())


    def run(self):
        self.__state = MngState.RUNNING
        self.__set_producer_task_que()
        while self.__state is not MngState.DONE:
            # self.__parent.notify(self, f"test event {test}")
            pass

    def notify(self, sender: object, event: str) -> None:
        pass
