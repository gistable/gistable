#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

from array import array
from collections import defaultdict
from datetime import datetime, time
from StringIO import StringIO
import sys


def mjd2datetime(payload):
    """ 修正ユリウス日を日本時間に変換する。ARIB STD-B10 第2部の付録Cをそのまま実装 """
    mjd = (payload[0] << 8) | payload[1]
    yy_ = int((mjd - 15078.2) / 365.25)
    mm_ = int((mjd - 14956.1 - int(yy_ * 365.25)) / 30.6001)
    k = 1 if 14 <= mm_ <= 15 else 0
    day = mjd - 14956 - int(yy_ * 	365.25) - int(mm_ * 30.6001)
    year = 1900 + yy_ + k
    month = mm_ - 1 - k * 12
    hour = ((payload[2] & 0xF0) >> 4) * 10 + (payload[2] & 0x0F)
    minute = ((payload[3] & 0xF0) >> 4) * 10 + (payload[3] & 0x0F)
    second = ((payload[4] & 0xF0) >> 4) * 10 + (payload[4] & 0x0F)
    return datetime(year, month, day, hour, minute, second)

def bcd2time(payload):
    """ 2進化10進数で表現された時刻データをdatetime.timeオブジェクトに変換 """
    hour = ((payload[0] & 0xF0) >> 4) * 10 + (payload[0] & 0x0F)
    minute = ((payload[1] & 0xF0) >> 4) * 10 + (payload[1] & 0x0F)
    second = ((payload[2] & 0xF0) >> 4) * 10 + (payload[2] & 0x0F)
    return time(hour, minute, second)

class TSFile(file):
    """ TransportStreamファイルオブジェクト。188バイトずつ読み込む """
    def next(self):
        packet = self.read(188)
        if not packet:
            raise StopIteration
        return Packet(StringIO(packet))

class Packet(object):
    def __init__(self, packet):
        self.header = Header(packet)
        if self.header.has_adaptation:
            self.adaptation = Adaptation(packet)
        if self.header.has_payload:
            self.payload = Payload(packet)

    def __getattr__(self, name):
        try:
            return self.header.__dict__[name]
        except NameError:
            try:
                self.adaptation.__dict__[name]
            except NameError, AttributeError:
                raise AttributeError

class Header(object):
    def __init__(self, packet):
        val = array('B', packet.read(4))
        self.sync = val[0]
        self.trans_error = (val[1] & 0x80) >> 7
        self.payload_start = (val[1] & 0x40) >> 6
        self.element_priority = (val[1] & 0x20) >> 5
        self.pid = ((val[1] & 0x1F) << 8) | val[2]
        self.scambling = (val[3] & 0xC0) >> 6
        self.has_adaptation = (val[3] & 0x20) >> 5
        self.has_payload = (val[3] & 0x10) >> 4
        self.index = (val[3] & 0x0F)

    def __str__(self):
        return ("Header(0x%02X, error=%d, start=%d, priority=%d, pid=0x%04X, "
                "scam=%d, adap=%d, payload=%d, index=%d)") % (
            self.sync, self.trans_error, self.payload_start,
            self.element_priority, self.pid, self.scambling,
            self.has_adaptation, self.has_payload, self.index)

class Adaptation(object):
    def __init__(self, packet):
        self.length = array('B', packet.read(1))[0]
        val = array('B', packet.read(1))[0]
        self.discontinuity = (val & 0x80) >> 7
        self.random_access = (val & 0x40) >> 6
        self.priority = (val & 0x20) >> 5
        self.has_pcr = (val & 0x10) >> 4
        self.has_opcr = (val & 0x08) >> 3
        self.splicing_point = (val & 0x04) >> 2
        self.transport_private = (val & 0x02) >> 1
        self.extension = val & 0x01

        val = array('B', packet.read(self.length))

    def __str__(self):
        return ("    Adaptation(len=%d, discon=%d, ram=%d, priority=%d, "
                "pcr=%d, opcr=%d, splicing=%d, private=%d, extension=%d)") % (
                self.length, self.discontinuity, self.random_access,
                self.priority, self.has_pcr, self.has_opcr,
                self.splicing_point, self.transport_private, self.extension)

def Payload(packet):
    return array('B', packet.read())

class Table(object):
    def __init__(self, payload):
        self.table_id = payload[1]
        self.section_syntax = (payload[2] & 0x80) >> 7
        self.length = ((payload[2] & 0x0F) << 8) | payload[3]
        self.id = (payload[4] << 8) | payload[5]
        if self.table_id not in(0x70, 0x71, 0x72):
            self.version = (payload[6] & 0x3E) >> 1
            self.current_next = payload[6] & 0x01
            self.section = payload[7]
            self.last_section = payload[8]
            self.crc = payload[-4:]

class EIT(Table):
    def __init__(self, payload):
        Table.__init__(self, payload)
        self.transport_id = (payload[9] << 8) | payload[10]
        self.original_network_id = (payload[11] << 8) | payload[12]
        self.segment_last_section = payload[13]
        self.last_table_id = payload[14]
        self.events = make_events(payload, 15, self.length - 15)

def make_events(payload, cur, length):
    events = []
    while cur < length:
        event_id = (payload[cur] << 8) | payload[cur+1]
        start = mjd2datetime(payload[cur+2:cur+7])
        duration = bcd2time(payload[cur+7:cur+10])
        status = (payload[cur+10] & 0xE0) >> 5
        scramble = (payload[cur+10] & 0x10) >> 4
        desc_length = ((payload[cur+10] & 0x0F) << 8) | payload[cur+11]
        descs = payload[cur+12:cur+12+desc_length]
        descriptors = make_descriptors(descs, 0, desc_length)
        cur += 12 + desc_length
        events.append(Event(event_id, start, duration, status,
                            scramble, descriptors))
    return events

def make_descriptors(payload, cur, length):
    descriptors = []
    while cur < length:
        desc_tag = payload[cur]
        cur += 1
        desc_length = payload[cur]
        descriptors.append({'tag': desc_tag, 'len': desc_length})
        cur += desc_length + 1

    return descriptors


class Event(object):
    def __init__(self, event_id, start, duration, status,
                       scramble, descriptors):
        self.event_id = event_id
        self.start = start
        self.duration = duration
        self.status = status
        self.scramble = scramble
        self.descriptors = descriptors

    def __str__(self):
        return "  Event(0x%04X, %s, %s, %d, %d)" % (
            self.event_id, self.start, self.duration, self.status,
            self.scramble)

class TSParser(object):
    # パース対象のPIDを指定
    table_map = {
        0x12: EIT,
        0x27: EIT,
    }

    def __init__(self, filename):
        self.tsfile = TSFile(filename)

    def get_table(self, pid, payload):
        cand = self.table_map[pid]
        return cand(payload)

    def parse(self):
        pes = defaultdict(list)
        buf = defaultdict(lambda: array('B', []))
        for packet in self.tsfile:
            if packet.pid in self.table_map and packet.has_payload:
                if packet.payload_start:
                    if packet.payload[0] == 0x00:
                        if buf[packet.pid]:
                            table = self.get_table(packet.pid, buf[packet.pid])
                            pes[packet.pid].append(table)
                        buf[packet.pid] = packet.payload
                    else:
                        buf[packet.pid] += packet.payload[1:]
                else:
                    buf[packet.pid] += packet.payload

        return pes

if __name__ == '__main__':
    filename = sys.argv[1]
    parser = TSParser(filename)
    pes = parser.parse()
    for pid, tables in pes.items():
        table_count = defaultdict(int)
        desc_count = defaultdict(int)
        for table in tables:
            table_count[table.table_id] += 1
            for event in table.events:
                for desc in event.descriptors:
                    desc_count[desc['tag']] += 1

        print 'pid 0x%04X' % pid
        for key, value in sorted(table_count.items()):
            print '0x%04X' % key, value
        print "-" * 20
        for key, value in sorted(desc_count.items()):
            print '0x%04X' % key, value
        print '=' * 20
