import threading
import time

from queue import Queue
from typing import List, cast

from clients.crawling_client.crawler_mng import CrawlerMng
from clients.dat_client.dat_mng import DatMng
from utils.manager import Manager
from utils.proxy.proxy import ProxyMng


class MainMng(Manager):

    def _init(self, *args, **kwargs):
        try:
            self.__proxy: ProxyMng = ProxyMng()
            kwargs: dict = {"parent": self}
            self.__crawlerMng: CrawlerMng = CrawlerMng(**kwargs)
            self.__managers: List[threading.Thread] = list()
            self.__managers.append(self.__crawlerMng)
        except Exception as e:
            raise e
        self.__que = Queue()

    def notify(self, sender: object, event: str) -> None:
        self.__que.put('sender = %s, event %s' % (sender.__class__.__name__, event))

        if sender.__class__.__name__ == "CrawlerMng":
            if event == "success":
                kwargs: dict = {"parent": self}
                dat_mng: DatMng = DatMng(**kwargs)
                dat_mng.task_que = cast(CrawlerMng, sender).ecode_que
                self.__managers.append(dat_mng)
        pass

    def run(self):
        # self.__crawlerMng.setDaemon(True)

        self.__crawlerMng.start()
        print(self.__crawlerMng.state)
        print(f"not done : {self.__crawlerMng.is_alive()}")
        while True:

            print("queue not empty : " + self.__que.get())
            print(f"not done : {self.__crawlerMng.is_alive()}")
            if self.__crawlerMng.state.__eq__("done") and self.__que.empty():
                print(f"done : {self.__crawlerMng.is_alive()}")
                break
            for mng in self.__managers:
                if not mng.is_alive():
                    self.__managers.remove(mng)

            if len(self.__managers) <= 0:
                break

            time.sleep(5)
            # if not self.__que.empty():
            #
            # else:
            #     print("queue empty")

        self.__crawlerMng.join()
