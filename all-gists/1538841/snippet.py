import time
import socket
def collect_metric(name, value, timestamp):
    sock = socket.socket()
    sock.connect( ("localhost", 2003) )
    sock.send("%s %d %d\n" % (name, value, timestamp))
    sock.close()

def now():
    return int(time.time())

collect_metric("metric.name", 42, now())
