import re
import socket
import struct
import logging
import subprocess
from fcntl import ioctl

SIOCGIFMTU = 0x8921
SIOCSIFMTU = 0x8922

log = logging.getLogger(__name__)

def get_mtu_for_address(ip):
    routeinfo = subprocess.check_output(['ip', 'route', 'get', ip])
    dev = re.search('.*dev (\w+) .*', routeinfo).groups()[0]
    mtuinfo = subprocess.check_output(['ip', 'link', 'show', dev])
    mtu = re.search('.*mtu ([0-9]+) .*', mtuinfo).groups()[0]
    return int(mtu)

class Iface:
    def __init__(self, ifname):
        self.ifname = ifname

    def get_mtu(self):
        '''Use socket ioctl call to get MTU size'''
        s = socket.socket(type=socket.SOCK_DGRAM)
        ifr = self.ifname + '\x00'*(32-len(self.ifname))
        try:
            ifs = ioctl(s, SIOCGIFMTU, ifr)
            mtu = struct.unpack('<H',ifs[16:18])[0]
        except Exception, s:
            log.critical('socket ioctl call failed: {0}'.format(s))
            raise

        log.debug('get_mtu: mtu of {0} = {1}'.format(self.ifname, mtu))
        self.mtu = mtu
        return mtu

    def set_mtu(self, mtu):
        '''Use socket ioctl call to set MTU size'''
        s = socket.socket(type=socket.SOCK_DGRAM)
        ifr = struct.pack('<16sH', self.ifname, mtu) + '\x00'*14
        try:
            ifs = ioctl(s, SIOCSIFMTU, ifr)
            self.mtu = struct.unpack('<H',ifs[16:18])[0]
        except Exception, s:
            log.critical('socket ioctl call failed: {0}'.format(s))
            raise

        log.debug('set_mtu: mtu of {0} = {1}'.format(self.ifname, self.mtu))

        return self.mtu


if __name__ == "__main__":
    import sys
    logging.basicConfig()

    mtu = None
    if len(sys.argv) > 2:
        dev,mtu = sys.argv[1:]
    elif len(sys.argv) > 1:
        dev = sys.argv[1]
    else:
        dev = 'eth0'

    iface = Iface(dev)
    if mtu is not None:
        iface.set_mtu(int(mtu))

    print dev,'mtu =',iface.get_mtu()