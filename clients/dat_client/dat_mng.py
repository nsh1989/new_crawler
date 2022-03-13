import datetime
import queue
import threading

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
            self.__set_token()
            self.__header = {
                'DAT-AuthorizationToken': self.__token,
            }
            self.__set_session()
            self.__token_created: datetime.datetime = datetime.datetime.now()
            self.__set_ecodes()
            # TODO 큐에서 리스트로 변환
            # TODO 리스트에서 VIN 정확하지 않은 값 (17자리)DROP
            # TODO 리스트에서 UNIQUE 리스트로 변경
            # TODO 리스트에서 원래 DB데이터와 중복 제거
            # TODO 리스트에 있는 VIN으로 유로파 코드 조회
            # TODO 조회 값 DB에 추가
            # TODO 조회 값 기존 값 DB 합체
            # TODO 큐 데이터 유로파 코드 조회
            # TODO 유로파 코드 적용 후 DB 업데이트

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

    def __check_database(self, data: dict) -> bool:
        # next(filter(lambda x: x.is_used is False, self.__producer_proxies))
        find = [row["ecode"] for row in self.__ecodes
                if row["badge"] is data["Badge"] and
                row["badgedetail"] is data["BadgeDetail"] and
                row["manufacturer"] is data["Manufacturer"] and
                row["transmission"] is data["Transmission"] and
                row["formYear"] is data["FormYear"] and
                row["fuelType"] is data["FuelType"] and
                row["model"] is data["Model"]
                ]
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

    def run(self):
        self.__state: MngState = MngState.RUNNING

        while self.__state is MngState.RUNNING:
            if self.__task_que.empty():
                continue
            data: dict = self.__task_que.get()
            try:
                time_delta = (datetime.datetime.now() - self.__token_created)
                minutes = time_delta.total_seconds() / 60
                if minutes >= 10:
                    self.__set_token()
                if self.__check_database(data):
                    DBMng.insert_dictionary("encarlist", data)
                else:
                    pass
            except Exception as e:
                print(e)
                self.__task_que.put(data)

        # todo dat token 갱신
        # todo taskque 만들기
        # todo consumer 만들기
        # todo consumer -> DB확인 -> 없으면 DAT 호출 -> DAT 있으면 dict추가 -> DB insert
        pass

    def notify(self, sender: object, event: str) -> None:
        self.__state = MngState.DONE
        pass
