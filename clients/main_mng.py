from utils.manager import Manager


class MainMng(Manager):

    def _init(self):
        pass

    # @property
    # def name(self):
    #     return self.__name
    #
    # @name.setter
    # def name(self, value: str):
    #     self.__name = value
    def get_size_consumers(self):
        return self._consumers

    def notify(self, sender: object, event: str) -> None:
        pass

    def execute(self):
        pass
