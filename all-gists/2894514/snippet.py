#! /usr/bin/env python
# avahi-alias.py

import avahi, dbus
from encodings.idna import ToASCII
import logging

# Got these from /usr/include/avahi-common/defs.h
CLASS_IN = 0x01
TYPE_CNAME = 0x05
TYPE_A = 0x01

TTL = 60

def publish_a_record(cname):
    logging.info('publish %s', cname)
    bus = dbus.SystemBus()
    server = dbus.Interface(bus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER),
            avahi.DBUS_INTERFACE_SERVER)
    group = dbus.Interface(bus.get_object(avahi.DBUS_NAME, server.EntryGroupNew()),
            avahi.DBUS_INTERFACE_ENTRY_GROUP)

    rdata = createRR(server.GetHostNameFqdn())
    cname = encode_dns(cname)

# 123         if (avahi_entry_group_add_address(entry_group, AVAHI_IF_UNSPEC, AVAHI_PROTO_UNSPEC, config->no_reverse ? AVAHI_PUBLISH_NO_REVERSE : 0, config->name, &config->address) < 0) {

    # socket.inet_aton('127.0.0.1')
    group.AddRecord(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, dbus.UInt32(0),
        cname, CLASS_IN, TYPE_A, TTL, '\x7f\x00\x00\x01')
    group.Commit()


def encode_dns(name):
    out = []
    for part in name.split('.'):
        if len(part) == 0: continue
        out.append(ToASCII(part))
    return '.'.join(out)

def createRR(name):
    out = []
    for part in name.split('.'):
        if len(part) == 0: continue
        out.append(chr(len(part)))
        out.append(ToASCII(part))
    out = ['127.0.0.1']
    out.append('\0')
    return ''.join(out)

if __name__ == '__main__':
    logging.basicConfig(level=20)
    import time, sys, locale
    for each in sys.argv[1:]:
        name = unicode(each, locale.getpreferredencoding())
        if not name.endswith('.local'):
            name = name + '.local'
        publish_a_record(name)
    try:
        # Just loop forever
        while 1: time.sleep(60)
    except KeyboardInterrupt:
        print "Exiting"
