from jsonrpclib import Server as ServerProxy
import base64
import jsonrpclib
import json

class AdminTrytonException(Exception):

    def __init__(self, result):
        self.result = result

    def __str__(self):
        return self.result

class AdminTryton(object):

    def __init__(self, url,tryton_admin_password):
        self._tryton_admin_password = tryton_admin_password
        self._server  = ServerProxy(url, verbose=0)

    def list_database(self):
        return self.__execute(method="list")

    def create_db(self, new_database_name, password_admin, lang):
        return self.__execute("create", new_database_name, \
            self._tryton_admin_password, lang, password_admin)

    def db_exist(self, db_name):
        return self.__execute(method="db_exist")

    def list_lang(self):
        return self.__execute(method="list_lang")

    def dump(self, database_name, name="out.dump"):
        data = self.__execute("dump", database_name, \
            self._tryton_admin_password)
        if data:
            with open(name,"wb") as f:
                f.write(base64.decodestring(data))
            return True
        else:
            return False

    def dump_to_string(self, database_name):
        return self.__execute("dump", database_name, \
            self._tryton_admin_password)

    def __execute(self, method, *args):
        server_exec = getattr(self._server.common.db, method)
        try:
            server_exec(None, None, *args)
        except TypeError:
            raise AdminTrytonException(self.__result())
        return self.__result()


    def __result(self):
        a = json.loads( jsonrpclib.history.response)
        return a.get("result", a.get("error"))

if __name__ == "__main__":
    try:
        a = AdminTryton("http://localhost:8000", "admin")
        #print a.list_database()
        #print a.list_lang()
        #print a.db_exist("aa1eeeeeeeee")
        #print a.dump_to_string("aa1")
        a.dump("aa1")
        #print a.create_db("test123","admin","en_EN")
    except AdminTrytonException as e:
        print e
