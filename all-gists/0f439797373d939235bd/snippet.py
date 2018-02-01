#
# For sending metric value to zabbix server.
#
# You must create item as "zabbix trapper" on server.
# Because the server must be connected to agent:10050, if it is selected "zabbix agent".
#
# Usage:
#    from modules.ZabbixSender import ZabbixSender
#    ZABBIX_HOST = "zabbix.example.com"
#    ZABBIX_PORT = 10051
#    sender = ZabbixSender(ZABBIX_HOST, ZABBIX_PORT)
#    sender.add("example-hostname-01", "healthcheck", 1)
#    sender.add("example-hostname-01", "item.keyname", 0.123)
#    sender.add("example-hostname-02", "item.keyname", 1234)
#    sender.send()
#

import socket
import struct
import time
import json

class ZabbixSender:

    log = True

    def __init__(self, host='127.0.0.1', port=10051):
        self.address = (host, port)
        self.data    = []

    def __log(self, log):
        if self.log: print log

    def __connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect(self.address)
        except:
            raise Exception("Can't connect server.")

    def __close(self):
        self.sock.close()

    def __pack(self, request):
        string = json.dumps(request)
        header = struct.pack('<4sBQ', 'ZBXD', 1, len(string))
        return header + string

    def __unpack(self, response):
        header, version, length = struct.unpack('<4sBQ', response[:13])
        (data, ) = struct.unpack('<%ds'%length, response[13:13+length])
        return json.loads(data)

    def __request(self, request):
        self.__connect()
        try:
            self.sock.sendall(self.__pack(request))
        except Exception as e:
            raise Exception("Failed sending data.\nERROR: %s" % e)

        response = ''
        while True:
            data = self.sock.recv(4096)
            if not data:
                break
            response += data

        self.__close()
        return self.__unpack(response)

    def __active_checks(self):
        hosts = set()
        for d in self.data:
            hosts.add(d['host'])

        for h in hosts:
            request = {"request":"active checks", "host":h}
            self.__log("[active check] %s" % h)
            response = self.__request(request)
            if not response['response'] == 'success': self.__log("[host not found] %s" % h)

    def add(self, host, key, value, clock=None):
        if clock is None: clock = int(time.time())
        self.data.append({"host":host, "key":key, "value":value, "clock":clock})

    def send(self):
        if not self.data:
            self.__log("Not found sender data, end without sending.")
            return False

        self.__active_checks()
        request  = {"request":"sender data", "data":self.data}
        response = self.__request(request)
        result   = True if response['response'] == 'success' else False

        if result:
            for d in self.data:
                self.__log("[send data] %s" % d)
            self.__log("[send result] %s" % response['info'])
        else:
            raise Exception("Failed send data.")

        return result

if __name__ == '__main__':
    sender = ZabbixSender()
    sender.add("gedowfather-example-01", "healthcheck", 1)
    sender.add("gedowfather-example-01", "gedow.item", 1111)
    sender.send()
