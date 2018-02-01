#!/usr/bin/env python3
from datetime import datetime
from urllib import request, error
from subprocess import check_output, CalledProcessError
from io import StringIO
from time import tzname, localtime
import socket

LOCAL_NET_URLS = {'r': 'http://192.168.1.1',
                  }
INTERNET_URLS = {'g': 'https://www.google.com',
                 'w': 'https://en.wikipedia.org',
                 'o': 'https://www.orange.pl',
                 'r': 'https://review.openstack.org/230275/',
                 }

# Is the network connected?
def check_network_connected():
    result = check_output(['nmcli', 'g'])
    return b'State: connected' in result

def check_url_python(url):
    """Quick check to see that the internet connection is up.

    Just makes sure we can reach the URL in question.
    Good for checking that the modem really is connected."""

    try:
        result = request.urlopen(url, timeout=5)
        return result.status >= 200 < 300
    except error.HTTPError as e:
        if e.code == 401:
            # A login redirect, that means it works.
            return True
    except (error.URLError, socket.error):
        return False
    
def check_url_wget(url):
    """Get the whole web page with resources.

    This checks that the site is practically loadable within a reasonable time.
    Good for when the internet connection is up, but the service is unrealiable,
    prone to load errors, or routing errors."""

    try:
        check_output(['wget', '-q', '-p', '-e', 'robots=off', '--timeout=15', '-P', '/tmp/ispstatus', '--no-cache', url])
        return True
    except CalledProcessError as e:
        if e.returncode in [0, 8]:
            return True
    return False

check_url = check_url_python

def check_local_area_network():
    """Check that the LAN is up"""
    for k, v in LOCAL_NET_URLS.items():
        yield k, check_url(v)

def check_internet():
    """Check that the WAN is up"""
    for k, v in INTERNET_URLS.items():
        yield k, check_url(v)

if __name__ == '__main__':
    tz = tzname[localtime().tm_isdst]
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' ' + tz
    #wifi = check_network_connected()
    lan = dict(check_local_area_network())
    internet = dict(check_internet())
    wifi_status = ''
    #wifi_status = 'wifi: OK  ' if wifi else 'wifi: DOWN'
    lan_status = 'lan: OK  ' if any(lan.values()) else 'lan: DOWN'
    ext_lan_status = '(%s)' % ''.join(sorted(k.upper() if v else k.lower() for k,v in lan.items()))
    internet_status = 'internet: OK  ' if all(internet.values()) else 'internet: DOWN'
    ext_internet_status = '(%s)' % ''.join(sorted(k.upper() if v else k.lower() for k,v in internet.items()))
    print(time, wifi_status, lan_status, ext_lan_status, internet_status, ext_internet_status)