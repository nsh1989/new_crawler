import trace
from dataclasses import dataclass
from typing import List

import requests as requests

from utils.patterns.singleton import Singleton


@dataclass
class Proxy:

    def __init__(self, value: str):
        attrs: List[str] = value.split(":")
        self.__ipaddr: str = attrs[0]
        self.__port: str = attrs[1]
        self.__id: str = attrs[2]
        self.__psw: str = attrs[3]
        self.__isUsed: bool = False
        self.__value: str = value

    def __del__(self):
        pass

    @property
    def value(self):
        return self.__value

    @property
    def ipaddr(self):
        return self.__ipaddr

    @property
    def port(self):
        return self.__port

    @property
    def id(self):
        return self.__id

    @property
    def psw(self):
        return self.__psw

    @property
    def is_used(self):
        return self.__isUsed

    @is_used.setter
    def is_used(self, value: bool):
        self.__isUsed = value


class ProxyMng(metaclass=Singleton):

    def __init__(self):
        if not self.__class__.is_instance():
            return
        super().__init__()
        self.__proxy_list: List[Proxy] = self.__setlist("https://wang.allpare.com/webshare.txt")

    @staticmethod
    def __setlist(url: str) -> List[Proxy]:
        s: requests.sessions = requests.session()
        resp: requests.models.Response = requests.models.Response()
        try:
            resp = s.get(url)
        except requests.exceptions as e:
            trace.Trace(e)
        if resp.status_code != 200:
            raise Exception(resp.status_code, "Could not connected to the proxy list server")

        return list(map(Proxy, list(filter(lambda x: len(str(x).split(':')).__eq__(4),
                                           list(filter(lambda x: not str(x).__eq__(''), resp.text.split("\r\n")))))))

    def get_proxy(self) -> Proxy:
        return self.__proxy_list.pop(0)
