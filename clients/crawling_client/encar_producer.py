import trace

import requests

from utils import Configs
from utils.patterns.producer_consumer import Producer
from utils.proxy.proxy import ProxyMng


class EncarProducer(Producer):

    def _init(self, *args, **kwargs):
        # self.__url: str = kwargs.get("url")
        self.__proxyMng: ProxyMng = ProxyMng()

    def run(self):
        self.__get_total_pages()
        pass

    @staticmethod
    def __get_total_pages() -> int:
        s: requests.session = requests.session()
        s.headers.update(Configs.headers[0])
        params = {
            'count': 'ture',
            'q': '(And.Hidden.N._.CarType.N._.Condition.Inspection._.Condition.Record.)',
            'sr': '|ModifiedDate|0|100'
        }
        resp: requests.models.Response = requests.models.Response()
        url = 'http://api.encar.com/search/car/list/premium'
        try:
            resp = s.get(url, params=params)
        except requests.exceptions as e:
            trace.Trace(e)
            raise e
        if resp.status_code != 200:
            raise Exception("Something is Wrong encar_producer __get_total_pages")

        return resp.json()['Count']

