from pymongo import Connection

class MongoCon(object):
    __db = None

    @classmethod
    def get_connection(cls):
        if cls.__db is None:
            cls.__db = Connection()
        return cls.__db