__cookies__ = ""
__X_CSRFToken = ""
__SAVE_DIR__ = "/var/www/IngressTracer"

import urllib
import urllib2
import zlib
import json
import time
import os


def request(url, data = ""):
    headers = {
        "Cookie": __cookies__,
        "X-CSRFToken": __X_CSRFToken,
        "User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.64 Safari/537.31",
    }
    if type(data) == dict:
        data = urllib.urlencode(data)
    request = urllib2.Request(url, data, headers)
    response = urllib2.urlopen(request)
    return response.read()

def getPaginatedPlextsV2(minTime,maxTime):
    print minTime,maxTime
    url = "http://www.ingress.com/rpc/dashboard.getPaginatedPlextsV2"
    data = {
  "desiredNumItems": 1000,
	"minLatE6": -86830198,
	"minLngE6": -180000000,
	"maxLatE6": 81057028,
	"maxLngE6": 180000000,
	"minTimestampMs": minTime,
	"maxTimestampMs": maxTime,
	"factionOnly": False,
	"ascendingTimestampOrder": False,
	"method": "dashboard.getPaginatedPlextsV2",
    }
    dt = request(url, json.dumps(data))
    return dt

def COMMfilter(data):
    rtn=[]
    for comm in data["result"]:
        if comm[2]["plext"]["plextType"]=="SYSTEM_BROADCAST":
            rtn.append(comm)
    return rtn

def getLast(data):
    maxTime=0
    for comm in data["result"]:
        if maxTime<comm[1]:
            maxTime=comm[1]
    if len(data["result"])<=0:
        return 0
    return maxTime

def run(startTime):
    dt=getPaginatedPlextsV2(startTime,1357000000000)
    print startTime,len(dt)
    lt=getLast(json.loads(dt))
    f=file(os.path.join(__base_dir__,"%s_%s.txt"%(startTime,lt)),"w")
    f.write(zlib.compress(dt,9))
    f.close()
    return lt

if __name__ == "__main__":
    t=1352984112622
    while t<1357000000000:
        t=run(t)
    

