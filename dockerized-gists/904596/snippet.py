import socket
import struct

class OptionError(Exception):
    """Configuration errors"""

class MasterServerQuery:
    def __init__(self, region='ALL_OVER', mserver=None, **kwargs):
        self.valid_regions = {'US_EAST': '\x00', 'US_WEST': '\x01', 'SOUTH_AMERICA': '\x02',
                              'EUROPE': '\x03', 'ASIA': '\x04', 'AUS': '\x05', 'MIDDLE_EAST': '\x06',
                              'AFRICA': '\x07', 'ALL_OVER': '\xFF'}

        self.valid_args = ['type', 'secure', 'gamedir', 'map', 'linux', 'empty',
                           'full', 'proxy', 'napp', 'noplayers', 'white']

        self.valid_mserver = {'hl1': (socket.gethostbyname('hl1master.steampowered.com'), 27010),
                              'hl2': (socket.gethostbyname('hl2master.steampowered.com'), 27011)}

        self._MSG_TYPE = '\x31'
        self._ZERO_IP = '\x30\x2E\x30\x2E\x30\x2E\x30\x3A\x30\x00'
        self._unpacker = struct.Struct('!BBBBH')
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.servers = []

        if region not in self.valid_regions:
            raise OptionError('Invalid region: %s' % region)
        else:
            self.region = self.valid_regions[region]

        if mserver not in self.valid_mserver:
            raise OptionError('Invalid master server: %s' % mserver)
        else:
            self.mserver = self.valid_mserver[mserver]

        self.options = ''
        if not kwargs:
            self.options='\x00'
        else:
            for x, y in kwargs.iteritems():
                if x not in self.valid_args:
                    raise OptionError('Invalid option: %s' % x)
                self.options += '\\%s\\%s' % (x, y)

    def get_last_ip(self, packed_ip):
        ip_tuple = self._unpacker.unpack(packed_ip)
        return '%s:%d' % ('.'.join([str(octet) for octet in ip_tuple[:4]]), ip_tuple[4])

    def get_next_packet(self, packed_ip):
        next_packet = '%c%c%s%s%c' % (self._MSG_TYPE, self.region,
                                      self.get_last_ip(packed_ip), self.options, '\x00')
        self._sock.send(next_packet)
    
    def format_server_list(self, packed_servers):
        ip_list = [self._unpacker.unpack(packed_servers[x:x+6]) for x in xrange(0, len(packed_servers), 6)]

        for server in ip_list:
            self.servers.append(('.'.join([str(octet) for octet in server[:4]]), server[4]))
    
    def get_server_list(self):
        initial_query = '%c%c%s%s%c' % (self._MSG_TYPE, self.region,
                                        self._ZERO_IP, self.options, '\x00')
        self._sock.connect(self.mserver)
        self._sock.send(initial_query)

        try:
            while True:
                print '%d' % len(self.servers)
                srv_recv = self._sock.recv(2048)
                if srv_recv.endswith('\x00\x00\x00\x00\x00\x00'): break
                self.format_server_list(srv_recv[6:])
                self.get_next_packet(srv_recv[-6:])
        except socket.error:
            self._sock.close()
            self._sock = None
        finally:
            self.format_server_list(srv_recv[6:])
            self._sock.close()
            self._sock = None

if __name__ == '__main__':
    a = MasterServerQuery('US_WEST', mserver='hl2', gamedir='tf', napp='500')
    a.get_server_list()
    print len(a.servers)
    print a.servers[:5]