import json
import queue
import random
import threading
import trace

import requests
from requests import Response

from utils import Configs
from utils.manager import Manager
from utils.patterns.producer_consumer import Producer
from utils.proxy.proxy import ProxyMng, Proxy
from clients.database_client.db_mng import DBMng


class EncarProducer(Producer):
    __url: str
    __parent: Manager
    __proxy: Proxy

    _lock = threading.Lock()

    def _init(self, *args, **kwargs):
        if len(kwargs) > 0:
            self.__url: str = kwargs.get("url")
            self.__parent: Manager = kwargs.get("parent")
            self.__proxy: Proxy = kwargs.get("proxy").pop()

    @property
    def url(self):
        return self.__url

    @property
    def proxy(self):
        return self.__proxy

    @proxy.setter
    def proxy(self, value: bool):
        self.__proxy = True

    def __checkID(self, id: int):
        self._lock.acquire()
        sql = "SELECT * FROM encarlist WHERE ID= %s;" % (id)
        rows = DBMng.get_all(sql)
        self._lock.release()
        if rows is None:
            return False
        if len(rows) > 0:
            return True
        else:
            return False

    def run(self):
        s: requests.session = requests.session()
        s.headers.update(Configs.headers[0])
        params = {
            'count': 'ture',
            'q': '(And.Hidden.N._.CarType.N._.Condition.Inspection._.Condition.Record.)',
            'sr': f'|ModifiedDate|{self.__url}|100'
        }
        resp: Response = Response()
        url = 'http://api.encar.com/search/car/list/premium'
        proxy = f"{self.__proxy.id}:{self.__proxy.psw}@{self.__proxy.ipaddr}:{self.__proxy.port}"
        proxies = {'https': f"socks5://{proxy}",
                   'http': f"socks5://{proxy}"
                   }
        items: dict = {}
        try:
            resp = s.get(url, params=params, proxies=proxies)
            items = resp.json()['SearchResults']
        except Exception as e:
            trace.Trace(e)
            self.__parent.notify(self, "http_error")
            return

        for item in items:
            dict = {}

            if item['ServiceCopyCar'] == 'DUPLICATION':
                continue

            if self.__checkID(item['Id']):
                continue

            dict['Id'] = item['Id']
            dict['Manufacturer'] = item['Manufacturer']
            dict['Model'] = item['Model']
            dict['Badge'] = str(item['Badge']).replace("'", "''")
            dict['BadgeDetail'] = ''
            try:
                dict['BadgeDetail'] = str(item['BadgeDetail']).replace("'", "''")
            except Exception as e:
                trace.Trace(e)
                pass
            dict['FuelType'] = item['FuelType']
            dict['Transmission'] = item['Transmission']
            dict['FormYear'] = item['FormYear']
            dict['FIRSTREG'] = item['Year']
            dict['Mileage'] = item['Mileage']
            dict['Price'] = item['Price']

            self.__parent.notify(self, json.dumps(dict))

        self.__parent.notify(self, "success")
