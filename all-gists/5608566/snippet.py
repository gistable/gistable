import jsonrpc
from jsonrpc import ServiceProxy
from os.path import expanduser
conf = {p[0]: p[1].strip() for p in 
    (l.split("=", 1) for l in open(expanduser("~/.bitcoin/bitcoin.conf")))
    if len(p) == 2}

proxy = ServiceProxy("http://%(rpcuser)s:%(rpcpassword)s@127.0.0.1:8332"%conf)
info = proxy.getinfo()