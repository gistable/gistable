import ssl
from requests.adapters import HTTPAdapter

CFG_FILE = '<path_to_cfg>'
secure_hosts = [
  'https://<host>'
]

class SSLAdapter(HTTPAdapter):
    def __init__(self, certfile, keyfile, password=None, *args, **kwargs):
        self._certfile = certfile
        self._keyfile = keyfile
        self._password = password
        return super(self.__class__, self).__init__(*args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=self._certfile,
                                keyfile=self._keyfile,
                                password=self._password)
        kwargs['ssl_context'] = context
        return super(self.__class__, self).init_poolmanager(*args, **kwargs)

def get_session():
    def get_config():
        with open(CFG_FILE) as reader:
            return json.load(reader)

    session = requests.Session()
    adapter = SSLAdapter(**get_config())

    for host in secure_hosts:
        session.mount(host, adapter)

    session.verify = False
    return session