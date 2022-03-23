import json

import threading

import requests
from requests import Response

from utils import Configs
from utils.manager import Manager
from utils.patterns.producer_consumer import Producer
from utils.proxy.proxy import Proxy
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
    def proxy(self, value: Proxy):
        self.__proxy = value

    def __check_id(self, encar_id: int):
        self._lock.acquire()
        sql = "SELECT * FROM encarlist WHERE ID= %s;" % encar_id
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
        resp: Response
        url = 'https://api.encar.com/search/car/list/premium'
        proxy = f"{self.__proxy.id}:{self.__proxy.psw}@{self.__proxy.ipaddr}:{self.__proxy.port}"
        proxies = {'https': f"socks5://{proxy}",
                   'http': f"socks5://{proxy}"
                   }

        try:
            resp = s.get(url, params=params, proxies=proxies)
            items = resp.json()['SearchResults']
        except Exception as e:
            print(e)
            self.__parent.notify(self, "http_error")
            return

        for item in items:

            consumer_task: dict = {}

            if item['ServiceCopyCar'] == 'DUPLICATION':
                continue

            if self.__check_id(item['Id']):
                continue

            consumer_task['Id'] = item['Id']
            consumer_task['Manufacturer'] = item['Manufacturer']
            consumer_task['Model'] = item['Model']
            consumer_task['Badge'] = str(item['Badge']).replace("'", "''")
            if 'BadgeDetail' in item:
                consumer_task['BadgeDetail'] = str(item['BadgeDetail']).replace("'", "''")

            else:
                consumer_task['BadgeDetail'] = ''
            # try:
            #
            # except Exception as e:
            #     with open("encar_producer_error.json", "a") as f:
            #         json_string = json.dumps(e)
            #         f.write(json_string)
            consumer_task['FuelType'] = item['FuelType']
            consumer_task['Transmission'] = item['Transmission']
            consumer_task['FormYear'] = item['FormYear']
            consumer_task['FIRSTREG'] = item['Year']
            consumer_task['Mileage'] = item['Mileage']
            consumer_task['Price'] = item['Price']

            self.__parent.notify(self, json.dumps(consumer_task))
        print(" encar producer end")
        self.__parent.notify(self, "success")
