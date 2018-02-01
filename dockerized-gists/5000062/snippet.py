import requests, hashlib, json

class API(object):
    def __init__(self, host, port, user, pw, salt="mysalt"):
        self.host = host
        self.port = port
        self.user = user
        self.pw = pw
        self.salt = salt
        self.url = "http://%s:%s/api/call" % (self.host, self.port)

    def call(self, method, *args):
        auth = hashlib.sha256("%s%s%s%s" % (self.user, method, self.pw, self.salt)).hexdigest()
        kwargs = {
            "method": method,
            "key": auth,
            "args": json.dumps(args)
        }
        print requests.get(self.url, params=kwargs).json

#x = API("localhost", 20059, "user", "password")
#x.call("system.getServerClockDebug")
