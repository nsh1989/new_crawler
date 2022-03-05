class Singleton(type):
    __instances = {}

    def is_instance(cls):
        if cls not in cls.__instances:
            return True
        return False

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        else:
            cls.__instances[cls].__init__(*args, **kwargs)
        return cls.__instances[cls]

    #
    # @classmethod
    # def __getInstance(cls):
    #     return cls.__instance
    #
    # @classmethod
    # def instance(cls, *args, **kargs):
    #     cls.__instance = cls(*args, **kargs)
    #     cls.__instance = cls.__getInstance
    #     return cls.__instance
