from __future__ import annotations

import json
import threading
from datetime import datetime
from dateutil import rrule
import requests
from requests import Response

from clients.database_client.db_mng import DBMng
from utils.manager import Manager
from utils.patterns.producer_consumer import Consumer
from utils.proxy.proxy import Proxy


class EncarConsumer(Consumer):
    __task: dict
    __parent: Manager
    __proxy: Proxy
    _lock = threading.Lock()

    @property
    def task(self):
        return self.__task

    @property
    def proxy(self):
        return self.__proxy

    @proxy.setter
    def proxy(self, value: proxy):
        self.__proxy = value

    def _init(self, *args, **kwargs):
        if len(kwargs) > 0:
            self.__task: dict = kwargs.get("task")
            self.__parent: Manager = kwargs.get("parent")
            self.__proxy: Proxy = kwargs.get("proxy").pop()

    def search_database(self, carid: int) -> dict | None:
        # self._lock.acquire()
        sql = "SELECT raw_data FROM call_history WHERE ID= %s;" % carid
        row = DBMng.get_one(sql)
        # self._lock.release()
        if row is None:
            return None
        else:
            return row

    def insert_database(self, carid: int, raw_data: dict):
        # self._lock.acquire()
        data: dict = {"id": carid,
                      "raw_data": json.dumps(raw_data)}
        DBMng.insert_dictionary(table_name="call_history", data=data)
        # self._lock.release()

    def __call_url(self, car_id: str, sd_flag: str = "N") -> dict | None:
        data = self.search_database(int(car_id))
        if data is None:
            url = f'https://www.encar.com/dc/dc_cardetailview.do'
            params = {
                'method': 'ajaxInspectView',
                'sdFlag': sd_flag,
                'rgsid': car_id
            }
            s: requests.session = requests.session()
            proxy = f"{self.__proxy.id}:{self.__proxy.psw}@{self.__proxy.ipaddr}:{self.__proxy.port}"
            proxies = {'https': f"socks5://{proxy}",
                       'http': f"socks5://{proxy}"
                       }
            resp: Response = Response()
            try:
                resp = s.get(url, params=params, proxies=proxies)
                self.insert_database(int(car_id), resp.json())
            except Exception as e:
                raise e
                # with open("encar_consumer_error.json", "a") as f:
                #     json_string = json.dumps(e)
                #     f.write(json_string)

            if resp.json()[0]['msg'] == 'FAIL':
                return None
            else:
                return resp.json()[0]['inspect']
        else:
            data = json.loads(data[0])
            if data[0]['msg'] == 'FAIL':
                return None
            else:
                return data[0]['inspect']

    def __set_detail(self, data: dict):
        self.__task['RAWDATA'] = data
        try:
            date = data['carSaleDto']['firstRegDt']['time']
            date = datetime.fromtimestamp(date / 1e3)
            self.__task['UPDATEDDATE'] = date
        except Exception as e:
            pass
            # with open("encar_consumer_error.json", "a") as f:
            #     json_string = json.dumps(e)
            #     f.write(json_string)
            # 매물변경일ss
        try:
            date = data['carSaleDto']['mdfDt']['time']
            date = datetime.fromtimestamp(date / 1e3)
            self.__task['ModifiedDate'] = date
        except Exception as e:
            pass
            # with open("encar_consumer_error.json", "a") as f:
            #     json_string = json.dumps(e)
            #     f.write(json_string)
        # 사고이력
        try:
            self.__task['ACCIDENT'] = data['direct']['inspectAccidentSummary']['accident']['code']
        except Exception as e:
            pass
            # with open("encar_consumer_error.json", "a") as f:
            #     json_string = json.dumps(e)
            #     f.write(json_string)
        # 수리이력
        try:
            self.__task['REPAIR'] = data['direct']['inspectAccidentSummary']['simpleRepair']['code']
        except Exception as e:
            pass
            # with open("encar_consumer_error.json", "a") as f:
            #     json_string = json.dumps(e)
            #     f.write(json_string)
        # vin
        try:
            if len(data['direct']['master']['carregiStration']) == 17:
                self.__task['VIN'] = data['direct']['master']['carregiStration']
        except Exception as e:
            pass
            # with open("encar_consumer_error.json", "a") as f:
            #     json_string = json.dumps(e)
            #     f.write(json_string)
        # AGE
        try:
            start_date = data['carSaleDto']['year']
            start_date = datetime.strptime(start_date, "%Y%m")
            end_date = self.__task['UPDATEDDATE']
            diff_list = list(rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=end_date))
            self.__task['AGE'] = len(diff_list)
        except Exception as e:
            pass
            # with open("encar_consumer_error.json", "a") as f:
            #     json_string = json.dumps(e)
            #     f.write(json_string)
        # SOLDDATE
        try:
            date = data['carSaleDto']['soldDt']['time']
            solddt = datetime.strptime(date, "%Y%m%d")
            self.__task['SOLDDATE'] = str(solddt)
            date = self.__task['SOLDDATE'] - self.__task['UPDATEDDATE']
            self.__task['SOLDDAYS'] = date
        except Exception as e:
            pass
            # with open("encar_consumer_error.json", "a") as f:
            #     json_string = json.dumps(e)
            #     f.write(json_string)

    def run(self):
        # self.__parent.notify(self, "success")
        data: dict
        try:
            data = self.__call_url(self.__task["Id"])
        except Exception as e:
            print(e)
            self.__parent.notify(self, "http_error")
            return
        if data is not None:
            self.__set_detail(data)
            self.__parent.notify(self, "success")
        else:
            self.__parent.notify(self, "none")
