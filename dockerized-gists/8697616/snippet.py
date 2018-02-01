#!/usr/bin/env python

import socket
from datetime import datetime
import csv
import sys
import pickle
import struct
import threading
import urllib2

"""Bulk loader for Akamai traffic reports csv -> Graphite"""

class CarbonIface(object):

    def __init__(self, host, port, event_url = None):
        '''Initialize Carbon Interface.
        host: host where the carbon daemon is running
        port: port where carbon daemon is listening for pickle protocol on host
        event_url: web app url where events can be added. It must be provided if add_event(...) is to
                   be used. Otherwise an exception by urllib2 will raise
        '''
        self.host = host
        self.port = port
        self.event_url = event_url
        self.__data = []
        self.__data_lock = threading.Lock()

    def add_data(self, metric, value, ts=None):
        if not ts:
            ts = time.time()
        if self.__data_lock.acquire():
            self.__data.append((metric, (ts, value)))
            self.__data_lock.release()
            return True
        return False

    def add_data_dict(self, dd):
        '''
        dd must be a dictionary where keys are the metric name,
        each key contains a dictionary which at least must have 'value' key (optionally 'ts')

        dd = {'experiment1.subsystem.block.metric1': {'value': 12.3, 'ts': 1379491605.55},
              'experiment1.subsystem.block.metric2': {'value': 1.35},
             ...}
        '''
        if self.__data_lock.acquire():
            for k,v in dd.items():
                ts = v.get('ts', time.time())
                value = v.get('value')
                self.__data.append((k, (ts, value)))
            self.__data_lock.release()
            return True
        return False
    def add_data_list(self, dl):
        '''
        dl must be a list of tuples like:
        dl = [('metricname', (timestamp, value)),
              ('metricname', (timestamp, value)),
              ...]
        '''
        if self.__data_lock.acquire():
            self.__data.extend(dl)
            self.__data_lock.release()
            return True
        return False

    def send_data(self, data=None):
        '''If data is empty, current buffer is sent. Otherwise data must be like:
        data = [('metricname', (timestamp, value)),
              ('metricname', (timestamp, value)),
              ...]
        '''
        save_in_error = False
        if not data:
            if self.__data_lock.acquire():
                data = self.__data
                self.__data = []
                save_in_error = True
                self.__data_lock.release()
            else:
                return False
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        payload = pickle.dumps(data)
        header = struct.pack("!L", len(payload))
        message = header + payload
        s.connect((self.host, self.port))
        try:
            s.send(message)
        except:
            println('Error when sending data to carbon')
            if save_in_error:
                self.__data.extend(data)
            return False
        else:
            print('Sent data to {host}:{port}: {0} metrics, {1} bytes'.format(len(data), len(message), host = self.host, port=self.port))
            return True
        finally:
            s.close()

    def add_event(self, what, data=None, tags=None, when=None):
        if not when: when = time.time()
        postdata = '{{"what":"{0}", "when":{1}'.format(what, when)
        if data: postdata += ', "data":"{0}"'.format(str(data))
        if tags: postdata += ', "tags": "{0}"'.format(str(tags))
        postdata += '}'
        req = urllib2.Request(self.url_post_event)
        req.add_data(postdata)

        try:
            urllib2.urlopen(req)
        except Exception, _:
            #log.exception('Error when sending event to carbon')
            pass

fields = [
    "time",
    "total_pageviews",
    "total_volume_in_mb",
    "edge_response_volume_in_mb",
    "midgress_response_volume_in_mb",
    "origin_response_volume_in_mb",
    "requests_volume_in_mb",
    "edge_requests",
    "midgress_requests",
    "origin_requests",
    "origin_requests_offload_percent",
    "origin_bandwidth_offload_percent",
    "edge_ok_requests",
    "edge_304_requests",
    "edge_redirect_requests",
    "edge_permission_requests",
    "edge_server_error_requests",
    "edge_client_abort_requests",
    "edge_other_requests",
    "edge_403_requests",
    "edge_404_requests",
    "origin_404_requests",
    "origin_ok",
    "origin_304_requests",
    "origin_redirect",
    "origin_permission",
    "origin_server_error_requests",
    "origin_other_requests"
]

field_map = { title:num for (num, title) in enumerate(fields) }

graphite_fields = [
    "edge_requests", "origin_requests", "origin_ok"
]

if __name__ == '__main__':

    carbon = CarbonIface("localhost", 2004)

    with open(sys.argv[1], 'rb') as csvfile:
        r = csv.DictReader(csvfile, fields)

        for row in r:
            if (row['time'].startswith("#")):
                continue

            ts = datetime.strptime(row['time'], "%m/%d/%Y %I:%M:%S %p").strftime("%s")

            for f in graphite_fields:
                carbon.add_data("dsd." + f, int(row[f]), int(ts))

            if r.line_num % 10 == 0:
                carbon.send_data()
                print r.line_num
