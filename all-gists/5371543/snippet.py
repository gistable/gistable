import json
from urllib2 import urlopen
import socket
from time import sleep

UDP_ADDRESS = "carbon.hostedgraphite.com"
UDP_PORT = 2003
RIAK_STATS_URL='http://localhost:11098/stats'

HG_API_KEY='Your Api Key from HostedGraphite.com'

stats=json.load(urlopen(RIAK_STATS_URL))

nn = stats['nodename'].replace('.', '-')
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP# Internet

for k in stats:
  if type(1) == type(stats[k]):
    message='%s.%s.%s %s' % (HG_API_KEY,nn,k,stats[k])
    sock.sendto(message, (UDP_ADDRESS, UDP_PORT))
    #sleep(0.1)
    print message
print 'Sent %s' % len(stats)