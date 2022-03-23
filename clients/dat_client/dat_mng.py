import datetime
import json
import queue
import threading
import time
from itertools import groupby

from clients.dat_client.datAPI import DAT
from clients.database_client.db_mng import DBMng
from utils.manager import Manager, MngState


class DatMng(Manager, threading.Thread):
    __token: str
    __session: str
    __ecodes: list
    __task_que: queue.Queue
    __state: MngState = MngState.START

    def _init(self, *args, **kwargs):
        try:
            self.__parent: Manager = kwargs.get("parent")
            self.__mode: str = kwargs.get("mode")
            self.__set_token()
            self.__header = {
                'DAT-AuthorizationToken': self.__token,
            }
            self.__set_session()
            self.__token_created: datetime.datetime = datetime.datetime.now()
            self.__set_ecodes()

        except Exception as e:
            print(e)
            DAT.get_token('1332560', 'parkwonb', 'parkwonb01', '1332560',
                          '268F665F1D8C348E98479B3C323839158F9B48D45EACE60426A4AFC68FA562F6')

    @property
    def task_que(self):
        return self.__task_que

    @task_que.setter
    def task_que(self, value: queue.Queue):
        self.__task_que = value

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, value: MngState):
        self.__state = value

    def __set_session(self):
        self.__session = DAT.make_session_id('1332560', 'parkwonb', '1332560',
                                             '268F665F1D8C348E98479B3C323839158F9B48D45EACE60426A4AFC68FA562F6',
                                             'FB9457B9BF60CEB375E18469EFD76519CEFD82ACCEC1E235611947ECB0C34EE5')

    def __set_token(self):
        self.__token = DAT.get_token('1332560', 'parkwonb', 'parkwonb01', '1332560',
                                     '268F665F1D8C348E98479B3C323839158F9B48D45EACE60426A4AFC68FA562F6')

    def __set_ecodes(self):
        self.__ecodes: list
        sql = "SELECT * FROM encarecode"
        self.__ecodes = DBMng.get_all(sql)
        # print(self.__ecodes)

    def __check_database(self, data: dict) -> bool:
        # next(filter(lambda x: x.is_used is False, self.__producer_proxies))
        find = self.get_ecode(data)
        if len(find) <= 0:
            return False
        data['ecode'] = find[0]
        return True

    @staticmethod
    def __make_ecode_data(data: dict) -> dict:
        ecode: dict = dict()
        ecode["badge"] = data["Badge"]
        ecode["badgedetail"] = data["BadgeDetail"]
        ecode["manufacturer"] = data["Manufacturer"]
        ecode["transmission"] = data["Transmission"]
        ecode["formYear"] = data["FormYear"]
        ecode["fuelType"] = data["FuelType"]
        ecode["model"] = data["Model"]
        return ecode

    def get_ecode(self, data: dict) -> list:
        find = [row["ecode"] for row in self.__ecodes
                if row["badge"] == data["badge"] and
                row["badgedetail"] == data["badgedetail"] and
                row["manufacturer"] == data["manufacturer"] and
                row["transmission"] == data["transmission"] and
                row["formyear"] == data["formyear"] and
                row["fueltype"] == data["fueltype"] and
                row["model"] == data["model"]
                ]
        return find

    @staticmethod
    def json_default(value):
        if isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
            return str(value)
        raise TypeError('not JSON serializable ' + value.__class__.name__)

    def __new_ecode_list(self, datalist: list):
        with open("encar_data.json", "w") as f:
            json_string = json.dumps(datalist, default=self.json_default)
            f.write(json_string)

        datalist = [row for row in datalist
                    if 'VIN' in row and len(row['VIN']) == 17
                    ]
        new_ecode: list = []
        for k, g in groupby(datalist, lambda x: (x["Badge"],
                                                 x["BadgeDetail"],
                                                 x["Manufacturer"],
                                                 x["Transmission"],
                                                 x["FormYear"],
                                                 x["FuelType"],
                                                 x["Model"],
                                                 x["VIN"])):
            new_ecode.append({"badge": k[0],
                              "badgedetail": k[1],
                              "manufacturer": k[2],
                              "transmission": k[3],
                              "formyear": k[4],
                              "fueltype": k[5],
                              "model": k[6],
                              "VIN": k[7]}
                             )
        # list({v['badge']: v for v in datalist}.values())
        with open("new_ecode_data.json", "w") as f:
            json_string = json.dumps(new_ecode)
            f.write(json_string)
        index = 0
        for data in new_ecode:
            index += 1
            find = self.get_ecode(data)
            # print(len(new_ecode))
            if len(find) > 0:
                new_ecode.remove(data)
                print(f"{index}: ecode exist " + str(data))
                continue
            else:
                time_delta = (datetime.datetime.now() - self.__token_created)
                minutes = time_delta.total_seconds() / 60
                if minutes >= 10:
                    self.__set_token()
                    self.__set_session()
                ecode: str
                ecode = DAT.get_ecode_by_vin(data['VIN'], self.__header, self.__session)
                if ecode is None:
                    data["ecode"] = ecode
                else:
                    data["ecode"] = ecode
            self.__ecodes.append(data)
            try:
                del data['VIN']
            except KeyError:
                pass
            DBMng.insert_dictionary("encarecode", data)
            print(f"{index}: DB insert " + str(data))

        with open("ecode_data.json", "w") as f:
            json_string = json.dumps(new_ecode)
            f.write(json_string)

    def run(self):

        # TODO 큐에서 리스트로 변환
        # TODO 리스트에서 VIN 정확하지 않은 값 (17자리)DROP
        # TODO 리스트에서 UNIQUE 리스트로 변경
        # TODO 리스트에서 원래 DB데이터와 중복 제거
        # TODO 리스트에 있는 VIN으로 유로파 코드 조회
        # TODO 조회 값 DB에 추가
        # TODO 조회 값 기존 값 DB 합체
        # TODO 큐 데이터 유로파 코드 조회
        # TODO 유로파 코드 적용 후 DB 업데이트
        while self.__state is MngState.START:
            if self.__mode == "DAT":
                with open("encar_data.json", "r") as f:
                    data = json.loads(f.read())
                    que: queue.Queue = queue.Queue()
                    [que.put(item) for item in data]
                    self.__task_que = que
                break
            time.sleep(10)

        self.__state: MngState = MngState.RUNNING
        datalist: list = [item for item in self.__task_que.queue]
        self.__new_ecode_list(datalist)

        while self.__state is MngState.RUNNING:
            if self.__task_que.empty():
                break
            data: dict = self.__task_que.get()
            data = dict((k.lower(), v) for k, v in data.items())
            try:
                if self.__check_database(data):
                    data['rawdata'] = json.dumps(data['rawdata'])
                    DBMng.insert_dictionary("encarlist", data)
                    print("Insert DB success")
                else:
                    pass
            except Exception as e:
                print(e)
                if e.args[0] != 1062:
                    self.__task_que.put(data)
        print("dat_mng done")

    def notify(self, sender: object, event: str) -> None:
        self.__state = MngState.DONE
        pass
