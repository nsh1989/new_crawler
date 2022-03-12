from __future__ import annotations

from datetime import datetime
from dateutil import rrule
import requests
from requests import Response

from utils.manager import Manager
from utils.patterns.producer_consumer import Consumer
from utils.proxy.proxy import Proxy


class EncarConsumer(Consumer):
    __task: dict
    __parent: Manager
    __proxy: Proxy

    @property
    def task(self):
        return self.__proxy

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

    def __call_url(self, car_id: str, sd_flag: str = "N") -> dict | None:
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

        resp: Response
        try:
            resp = s.get(url, params=params, proxies=proxies)
        except Exception as e:
            raise e

        if resp.json()[0]['msg'] == 'FAIL':
            return None
        else:
            return resp.json()[0]['inspect']

    def __set_detail(self, data: dict):
        self.__task['RAWDATA'] = data
        try:
            date = data['carSaleDto']['firstRegDt']['time']
            date = datetime.fromtimestamp(date / 1e3)
            self.__task['UPDATEDDATE'] = date
        except Exception as e:
            print("매물 최초등록일")
            print(e)
            # 매물변경일
            try:
                date = data['carSaleDto']['mdfDt']['time']
                date = datetime.fromtimestamp(date / 1e3)
                self.__task['ModifiedDate'] = date
            except Exception as e:
                print("매물 변경일")
                print(e)
            # 사고이력
            try:
                self.__task['ACCIDENT'] = data['direct']['inspectAccidentSummary']['accident']['code']
            except Exception as e:
                print("사고이력")
                print(e)
            # 수리이력
            try:
                self.__task['REPAIR'] = data['direct']['inspectAccidentSummary']['simpleRepair']['code']
            except Exception as e:
                print("수리이력")
                print(e)
            # vin
            try:
                if len(data['direct']['master']['carregiStration']) == 17:
                    self.__task['VIN'] = data['direct']['master']['carregiStration']
            except Exception as e:
                print("VIN")
                print(e)
            # AGE
            try:
                start_date = data['carSaleDto']['year']
                start_date = datetime.strptime(start_date, "%Y%m")
                end_date = self.__task['UPDATEDDATE']
                diff_list = list(rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=end_date))
                self.__task['AGE'] = len(diff_list)
            except Exception as e:
                print("AGE")
                print(e)
            # SOLDDATE
            try:
                date = data['carSaleDto']['soldDt']['time']
                solddt = datetime.strptime(date, "%Y%m%d")
                self.__task['SOLDDATE'] = str(solddt)
                date = self.__task['SOLDDATE'] - self.__task['UPDATEDDATE']
                self.__task['SOLDDAYS'] = date
            except Exception as e:
                print("SOLDDATE")
                print(e)

    def run(self):
        self.__parent.notify(self, "success")
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
