import json

import threading
import time
import trace

from queue import Queue
from typing import List, cast

import requests
from requests import Response

from clients.crawling_client.encar_consumer import EncarConsumer
from clients.crawling_client.encar_producer import EncarProducer
from utils import Configs
from utils.manager import Manager, MngState
from utils.patterns.producer_consumer import Consumer, Producer
from utils.proxy.proxy import ProxyMng, Proxy


class CrawlerMng(Manager, threading.Thread):
    __state: MngState
    __producerNum: int = 5
    __consumerNum: int = 5

    def _init(self, *args, **kwargs):

        self.__proxyMng: ProxyMng = ProxyMng()
        self.__parent = kwargs.get("parent")
        self.__state = MngState.START

        self._producers: List[Producer] = list()
        self.__producerTaskQue: Queue = Queue()
        self.__producer_proxies: List[Proxy] = list()

        self._consumers: List[Consumer] = list()
        self.__consumerTaskQue: Queue = Queue()
        self.__consumer_proxies: List[Proxy] = list()

    @property
    def state(self):
        return self.__state

    @property
    def consumer_task_que(self):
        return self.__consumerTaskQue

    def __set_producer_task_que(self):
        s: requests.session = requests.session()
        s.headers.update(Configs.headers[0])
        params = {
            'count': 'ture',
            'q': '(And.Hidden.N._.CarType.N._.Condition.Inspection._.Condition.Record.)',
            'sr': '|ModifiedDate|0|100'
        }
        resp: Response
        url = 'https://api.encar.com/search/car/list/premium'
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
            proxy: Proxy = self.__proxyMng.get_proxy()
            proxy.is_used = True
            self.__producer_proxies.append(proxy)
            kwargs = {"url": i, "parent": self, "proxy": [proxy]}
            producer = EncarProducer(**kwargs)
            producer.setName(f"producer_{i}")
            producer.setDaemon(True)
            self._producers.append(producer)
        for producer in self._producers:
            producer.start()
            print(f"{producer.getName()} is alive {producer.is_alive()}")

        for i in range(0, self.__consumerNum):
            proxy = self.__proxyMng.get_proxy()
            proxy.is_used = False
            self.__consumer_proxies.append(proxy)
            self._consumers.append(EncarConsumer())

    def __check_producers(self):

        if len(self.__producer_proxies) < 5:
            self.__producer_proxies.append(self.__proxyMng.get_proxy())
        for producer in self._producers:
            if producer.is_alive() is False:
                self._producers.remove(producer)
                if not self.__producerTaskQue.empty():
                    proxy: Proxy
                    if len(self.__producer_proxies) > 0:
                        proxy = next(filter(lambda x: x.is_used is False, self.__producer_proxies))
                    else:
                        proxy = self.__proxyMng.get_proxy()
                        self.__producer_proxies.append(proxy)
                    kwargs = {"url": self.__producerTaskQue.get(), "parent": self, "proxy": [proxy]}
                    new_producer = EncarProducer(**kwargs)
                    self._producers.append(new_producer)
                    new_producer.start()

    def __check_consumers(self):
        for consumer in self._consumers:
            if not self.consumer_task_que.empty():
                if consumer.is_alive() is False:
                    self._consumers.remove(consumer)
                    self.__make_consumers()
                else:
                    break
            else:
                break

    def __make_consumers(self):
        # if len(self.__consumer_proxies) < 5:
        #     self.__consumer_proxies.append(self.__proxyMng.get_proxy())
        if not self.consumer_task_que.empty() and not len(self._consumers) < 5:
            proxy: Proxy
            if len(self.__consumer_proxies) == 5:
                proxy = next(filter(lambda x: x.is_used is False, self.__consumer_proxies))
            else:
                proxy = self.__proxyMng.get_proxy()
                self.__consumer_proxies.append(proxy)
            proxy.is_used = True
            data: str = self.consumer_task_que.get()
            data: dict = json.loads(data)
            kwargs = {"task": data, "parent": self, "proxy": [proxy]}
            consumer = EncarConsumer(**kwargs)
            consumer.setDaemon(True)
            self._consumers.append(consumer)
            consumer.start()

    def run(self):
        self.__state = MngState.RUNNING
        self.__set_producer_task_que()
        self.__set_producers_consumers()

        while self.__state is not MngState.DONE:
            time.sleep(2)
            if self.__check_tasks_done():
                self.__state = MngState.DONE
                break
            self.__check_producers()
            self.__check_consumers()

    def __check_tasks_done(self) -> bool:
        if len(self._producers) <= 0 and self.__producerTaskQue.empty() and len(
                self._consumers) <= 0 and self.__consumerTaskQue.empty():
            return True
        else:
            return False

    def notify(self, sender: object, event: str) -> None:

        if sender.__class__.__name__ == "EncarProducer":
            sender: EncarProducer = cast(EncarProducer, sender)
            self.__producer_notify(sender, event)
        elif sender.__class__.__name__ == "EncarConsumer":
            sender: EncarConsumer = cast(EncarConsumer, sender)
            self.__consumer_notify(sender, event)
        pass

    def __consumer_notify(self, sender: EncarConsumer, event: str):
        if event == "http_error":
            self.__consumer_proxies.remove(sender.proxy)
            self.__consumerTaskQue.put(sender.task)
            self.__check_consumers()
            return
        elif event == "success":
            sender.proxy.is_used = False
        elif event == "none":
            pass
        # else:
        # self.__consumerTaskQue.put(event)

    def __producer_notify(self, sender: EncarProducer, event: str):
        if event == "http_error":
            self.__producer_proxies.remove(sender.proxy)
            self.__producerTaskQue.put(sender.url)
        elif event == "success":
            sender.proxy.is_used = False
        else:
            self.__consumerTaskQue.put(event)
