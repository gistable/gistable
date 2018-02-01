# zabbix_get.py : Python port of zabbix_get
# http://www.zabbix.com/documentation/1.8/protocols/agent
# http://www.zabbix.com/wiki/doc/tech/proto/zabbixagentprotocol

import argparse
import socket
import struct
import sys

def str2packed(data):
    header_field =  struct.pack('<4sBQ', 'ZBXD', 1, len(data))
    return header_field + data

def packed2str(packed_data):
    header, version, length = struct.unpack('<4sBQ', packed_data[:13])
    (data, ) = struct.unpack('<%ds'%length, packed_data[13:13+length])
    return data

def zabbix_get(args):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((args.host, args.port))
    s.sendall(str2packed(args.key))

    data = ''
    while True:
        buff = s.recv(1024)
        if not buff:
            break
        data += buff

    response = packed2str(data)

    s.close()
    return response

def main():
    parser = argparse.ArgumentParser(prog='PROG')
    parser.add_argument('--host', help='Specify host name or IP address of a host')
    parser.add_argument('--port', type=int, default=10050, help='Specify port number of agent running on the host. Default is 10050')
    parser.add_argument('--key', help='Specify key of item to retrieve value for')
    args =  parser.parse_args()

    print zabbix_get(args)

if __name__ == '__main__':
    main()