from __future__ import print_function
import argparse
import requests  # pip install requests
import sys
from jsonrpclib import jsonrpc  # pip install jsonrpclib-pelix


"""
Simple script to throttle nzb clients for plexpy

There are 3 params:
-t {duration}
-sc {streams}
-a {action}

no arguments will simply reduce the speed

It can also be used as a commandline tool:
python throttle_nzbclient.py -c sabnzbd -h 10.0.0.97 -p 8085 -api 1234 -t 60 # pauses sab for 60 minutes  

"""

#### Edit vars ####
i_use = 'sabnzbd'  # or 'nzbget'
reduce_speed_to = 1000  # in kbit\s
max_speed = 10000  # bandwidth from isp in kbits
pause_for = None  # int minutes or None to disable
remote_transcode_speed = None  # remote transcode session speed in plex or None to disable
max_transcode_sessions = None  # Number of streams before we do something, int or None to disable


sabnzbd_host = 'localhost'
sabnzbd_port = 8080
sabnzbd_apikey = '' # string
sabnzbd_ssl = False # True or False
sabnzbd_webdir = '/sabnzbd/' # Default is '/sabnzbd/'

nzbget_host = 'localhost'
nzbget_port = 6789
nzbget_username = 'nzbget' # Default username
nzbget_password = 'tegbzn6789 ' # default password
nzbget_ssl = False # True or False
nzbget_webdir = '/' # default webdir is '/'
#### Edit stop ####

action = None  # Dont edit me


class Sab(object):
    def __init__(self, apikey, host,
                 port, ssl, webdir):

        ssl = 's' if ssl else ''
        self.url = 'http%s://%s:%s%sapi?output=json&apikey=%s&' % (ssl, host, port, webdir, apikey)

    def changespeed(self, speed):
        print("Changed sabznbd speed to %s" % speed)
        return self.request('mode=config&name=speedlimit&value=' + str(speed))

    def pause_for(self, minutes):
        print("Pausing sabnzbd for %s minutes" % minutes)
        return self.request('mode=config&name=set_pause&value=' + str(minutes))

    def restart(self):
        print('Restarting Sabznbd')
        return self.request('mode=restart')

    def resume(self):
        print('Resuming downloading with sabznbd')
        return self.request('mode=resume')

    def shutdown(self):
        print('Shutting down Sabznbd')
        return self.request('mode=shutdown')

    def status(self):
        pass  # todo

    def request(self, s):
        try:
            requests.get(self.url + s)
        except Exception as e:
            print('Failed to do %s' % (s, e))


class Nzbget(object):
    def __init__(self, username, password, host, port, ssl, webdir):
        if username and password:
            authstring = '%s:%s@' % (username, password)
        else:
            authstring = ''

        ssl = 's' if ssl else ''
        self.url = 'http%s://%s%s:%s%sjsonrpc' % (ssl, authstring, host, port, webdir)
        self.action = jsonrpc.ServerProxy(self.url)

    def pause(self):
        print('Paused nzbget')
        return self.action.pause()

    def changespeed(self, speed):
        print("Changed speed to %s kbit\'s" % speed)
        return self.action.rate(int(speed))

    def pause_for(self, sec):
        self.pause()
        mins = int(sec) * 60
        self.action.scheduleresume(mins)  # convert from minutes to sec
        print('for %s' % mins)

    def resume(self):
        print('Resumed download for nbzbget')
        return self.action.resume()

    def shutdown(self):
        print('Shutting down nbzbget')
        return self.action.shutdown()

    def status(self):
        pass  # todo


if __name__ == '__main__':
    if i_use == 'sabnzbd' and 'nzbget' not in sys.argv:
        client_host = sabnzbd_host
        client_port = sabnzbd_port
        client_apikey = sabnzbd_apikey
        client_ssl = sabnzbd_ssl
        client_webdir = sabnzbd_webdir
        client_username = None
        client_password = None
    else:
        client_host = nzbget_host
        client_port = nzbget_port
        client_username = nzbget_username
        client_password = nzbget_password
        client_ssl = nzbget_ssl
        client_apikey = None
        client_webdir = nzbget_webdir

    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--client', action='store', default=i_use,
                        help='Choose download client, sabznbd or nzbget')

    parser.add_argument('-sc', '--stream_count', action='store', default=0, type=int,
                        help='stream_count argument from plexpy')

    parser.add_argument('-s', '--speed', action='store', default=reduce_speed_to, type=int,
                        help='Reduce download speed to')

    parser.add_argument('-a', '--action', action='store', default=None,
                        help='notify_action argument from plexpy')

    parser.add_argument('-t', '--time', action='store', default=pause_for, type=int,
                        help='Number of minutes the client is paused')

    parser.add_argument('-host', '--host', action='store', default=client_host,
                        help='host for the nzb client')

    parser.add_argument('-p', '--port', action='store', default=client_port,
                        help='port for the nzb client')

    parser.add_argument('-api', '--apikey', action='store', default=client_apikey,
                        help='sabnzbd apikey')

    parser.add_argument('-u', '--username', action='store', default=client_username,
                        help='username nzbget')

    parser.add_argument('-pass', '--password', action='store', default=client_password,
                        help='password nzbget')

    parser.add_argument('-wd', '--webdir', action='store', default=client_webdir,
                        help='password nzbget')

    parser.add_argument('-ssl', '--ssl', action='store_true', default=client_ssl,
                        help='Does the the nzb client use ssl?')

    parser.add_argument('-ms', '--max_speed', action='store', default=max_speed,
                        help='Max speed of your internet connection in kbits')

    parser.add_argument('-rts', '--remote_transcode_speed', action='store', default=remote_transcode_speed,
                        help='Max speed of your internet connection in kbits')

    parser.add_argument('-mts', '--max_transcode_sessions', action='store', default=max_transcode_sessions,
                        help='Number of max streams before we reduce the speed')

    p = parser.parse_args()

    if p.client == 'sabnzbd':
        client = Sab(host=p.host, port=p.port, apikey=p.apikey, ssl=p.ssl, webdir=p.webdir)
    else:
        client = Nzbget(host=p.host, port=p.port,
                        username=p.username, password=p.password,
                        ssl=p.ssl, webdir=p.webdir)

    if p.time:
        # should this be added to a current pause or add to current pause?
        client.pause_for(p.time)

    if p.stream_count:
        if p.stream_count and p.remote_transcode_speed:
            pass  # todo
        if int(p.streamcount) >= int(p.max_transcode_sessions):
            client.changespeed(p.speed)
        else:
            client.changespeed(p.max_speed)

    if p.action:
        if p.action in ('play', 'resume'):
            client.changespeed(p.speed)
        elif p.action == 'buffer':
            client.pausefor(15)
        elif p.action in ('stop', 'pause'):
            client.changespeed(p.max_speed)

