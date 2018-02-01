import logging
import urllib2
import re
from contextlib import closing

def get_ip(url = "http://checkip.dyndns.org/"):
    '''Get local machine (or router)'s external IP from a IP checking web
    service.

    url: the URL of the IP checking service. Default to
    http://checkip.dyndns.org/
    '''
    with closing(urllib2.urlopen(url)) as f:
        b = f.read()
        # trim off htmls
        b = re.sub(r'.*\<body\>(.*)\</body\>.*', r'\1', b)
        ip = re.findall(r'\d+\.\d+\.\d+\.\d+', b)[0]
        logging.info("Current IP: {}".format(ip))
        return ip
