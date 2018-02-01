import requests
import json
from datetime import datetime, timedelta
import time
import logging
import argparse

BASE_URL = 'https://api.twitch.tv/kraken/'
CLIENTID = '<add your API key here>'

def start_logging(logfile='log.txt'):
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
            
    ch  = logging.StreamHandler()
    fh = logging.FileHandler(logfile)
    log.addHandler(ch)
    log.addHandler(fh)        
    
    requests_log = logging.getLogger("requests")
    requests_log.setLevel(logging.WARNING)

def get_viewers(stream_name):
    url = '{0}streams/{1}?client_id={2}'.format(BASE_URL, stream_name, CLIENTID)
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception("API returned {0}".format(r.status_code))
    infos = r.json()
    stream = infos['stream']
    results = {}
    if not stream:
        results = {'online':False,'title':None,'viewers':0}
    else:
        viewers = stream['viewers']
        title = stream['channel']['status']
        results = {'online':True,'title':title,'viewers':viewers}

    results['time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    results['stream'] = stream_name
    return results

def constant_polling(stream, onint=1,offint=5):
    logging.info("starting polling, inteval is " + 
        "{0}min (online) and {1}min (offline)".format(onint, offint))
    while True:
        online = False
        try:
            res = get_viewers(stream)            
            online = res['online']
            txt = json.dumps(res) 
            logging.info("Streamviewercount: {0}".format(txt))
        except Exception as e:
            logging.warn("Polling failed: {0}".format(e))            
        
        sleep_interval = onint if online else offint
        time.sleep(60*sleep_interval)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='log viewer rating of twitch' +
            ' stream')
    parser.add_argument('channel', help='channel name')
    parser.add_argument('--int_on', help='interval if online (min)', default=1)
    parser.add_argument('--int_off', help='interval if offline (min)', default=5)
    args = parser.parse_args()
    start_logging()
    constant_polling(args.channel, args.int_on, args.int_off)
        
