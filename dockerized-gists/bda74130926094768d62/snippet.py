#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import urllib2
import json
import os
import tempfile
import codecs
from optparse import OptionParser


def get_stats(url, requests, formatters):
    """
    指定された endpoint に接続して統計情報を sensu plugin 形式で取得する
    """
    payload = json.dumps(requests)
    req = urllib2.Request(url, headers={'Content-Type': 'application/json'})
    res = urllib2.urlopen(req, payload)

    keys = formatters.keys()
    ret = []

    def load_stat(key):
        formatter = formatters[key]
        stat = formatter.get_stat(f['value'], f['timestamp'])
        if isinstance(stat, list):
            ret.extend(stat)
        else:
            ret.append(stat)

    for f in json.loads(res.read()):
        attr = f['request']['attribute']
        if attr in keys:
            load_stat(attr)

        mbean = f['request']['mbean']
        if mbean in keys:
            load_stat(mbean)

    return ret


def print_stat(stat, output_format):
    """
    統計情報をそのまま出力する
    """
    print output_format % (stat['key'], stat['value'], stat['timestamp'])


def print_diff_stat(stat, previous_stat, output_format):
    """
    統計情報を前回の差分値との比較で出力する

    0 を出力する条件
    - 保存値が無い場合
    - 保存値があっても該当キーが無かった場合
    - 前回のタイムスタンプ値との差が 2 分以上の場合
    - 差分が 0 以下の時 (再起動の場合など)
    """
    if previous_stat is None:
        print output_format % (stat['key'], 0, stat['timestamp'])
    else:
        if stat['timestamp'] - previous_stat['timestamp'] > 120:
            print output_format % (stat['key'], 0, stat['timestamp'])
        else:
            value = max(stat['value'] - previous_stat['value'], 0)
            print output_format % (stat['key'], value, stat['timestamp'])


def print_stats(stats):
    """
    前回取得した値との差分を出力する

    0 を出力する条件
    - 保存値が無い場合
    - 保存値があっても該当キーが無かった場合
    - 前回のタイムスタンプ値との差が 2 分以上の場合
    """
    json_path = get_json_path()
    previous = None
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            saved_stats = json.load(f, 'utf-8')
        previous = dict([(saved['key'], saved) for saved in saved_stats])

    no_saved_data = previous is None
    # format を変更する必要が出たときには mackerel formatter に設定し、json に吐き出すようにする
    output_format = '%s\t%d\t%d'
    for stat in stats:
        if stat['delta']:
            previous_stat = None if no_saved_data else previous.get(stat['key'])
            print_diff_stat(stat, previous_stat, output_format)
        else:
            print_stat(stat, output_format)

    print


def save_stats(stats):
    """
    今回取得した統計情報を保存する
    """
    stats_json = get_json_path()
    with codecs.open(stats_json, 'w', 'utf-8') as f:
        json.dump(stats, f, indent=2, sort_keys=True, ensure_ascii=False)


def get_json_path():
    op = os.path
    basedir = op.join(tempfile.gettempdir(), 'mackerel-custom-agent')
    if not op.exists(basedir):
        os.makedirs(basedir)

    return op.splitext(op.join(basedir, op.basename(__file__)))[0] + '.json'


def main(argv, formatters):
    parser = OptionParser("usage: %prog [options]")
    parser.add_option("-u", "--url", metavar="URL", action="store", type="string", dest="url",
                      default="http://localhost:8778/jolokia/",
                      help="jolokia endpoint url")
    parser.add_option("-c", "--collector", metavar="COLLECTOR", action="store", type="string", dest="collector",
                      default="MarkSweepCompact",
                      help="garbage collector type")

    (options, args) = parser.parse_args(argv)

    requests_map = {
        'MarkSweepCompact': JOLOKIA_REQUESTS_MSC,
        'ParallelScavenge': JOLOKIA_REQUESTS_PS,
        'ConcMarkSweep': JOLOKIA_REQUESTS_CMS,
    }

    try:
        stats = get_stats(options.url, requests_map[options.collector], formatters)
        print_stats(stats)
        save_stats(stats)
    except urllib2.HTTPError, e:
        sys.stderr.write(e.msg)
        sys.exit(1)


class MackerelFormatter(object):

    prefix = ''

    def __init__(self, label, converter=None, delta=False):
        self.label = label
        self.converter = converter
        self.delta = delta

    def get_stat(self, value, timestamp):
        if self.converter:
            value = self.converter(value)
        key = '%s.%s' % (self.__class__.prefix, self.label,)
        return {
            'key': key,
            'value': value,
            'timestamp': timestamp,
            'delta': self.delta,
        }


class MackerelHeapFormatter(MackerelFormatter):

    def get_stat(self, value, timestamp):
        if self.converter:
            value = self.converter(value)
        key_prefix = '%s.%s' % (self.__class__.prefix, self.label,)
        return [
            {
                'key': key_prefix + '_used',
                'value': value['used'],
                'timestamp': timestamp,
                'delta': self.delta,
            },
            {
                'key': key_prefix + '_committed',
                'value': value['committed'],
                'timestamp': timestamp,
                'delta': self.delta,
            },
            {
                'key': key_prefix + '_free',
                'value': max(value['committed'] - value['used'], 0),
                'timestamp': timestamp,
                'delta': self.delta,
            },
        ]



JOLOKIA_REQUESTS_BASE = [
    {
        'type': 'read',
        'mbean': 'java.lang:name=Metaspace,type=MemoryPool',
        'attribute': 'Usage',
    },
    {
        'type': 'read',
        'mbean': 'java.lang:name=Compressed Class Space,type=MemoryPool',
        'attribute': 'Usage',
    },
    {
        'type': 'read',
        'mbean': 'java.lang:name=Code Cache,type=MemoryPool',
        'attribute': 'Usage',
    },
    {
        'type': 'read',
        'mbean': 'java.lang:type=Memory',
        'attribute': 'HeapMemoryUsage'
    },
    {
        'type': 'read',
        'mbean': 'java.lang:type=Memory',
        'attribute': 'NonHeapMemoryUsage'
    },
]

JOLOKIA_REQUESTS_MSC = JOLOKIA_REQUESTS_BASE + [
    {
        'type': 'read',
        'mbean': 'java.lang:name=Eden Space,type=MemoryPool',
        'attribute': 'Usage',
    },
    {
        'type': 'read',
        'mbean': 'java.lang:name=Survivor Space,type=MemoryPool',
        'attribute': 'Usage',
    },
    {
        'type': 'read',
        'mbean': 'java.lang:name=Tenured Gen,type=MemoryPool',
        'attribute': 'Usage',
    },
]

JOLOKIA_REQUESTS_PS = JOLOKIA_REQUESTS_BASE + [
    {
        'type': 'read',
        'mbean': 'java.lang:name=PS Eden Space,type=MemoryPool',
        'attribute': 'Usage',
    },
    {
        'type': 'read',
        'mbean': 'java.lang:name=PS Survivor Space,type=MemoryPool',
        'attribute': 'Usage',
    },
    {
        'type': 'read',
        'mbean': 'java.lang:name=PS Old Gen,type=MemoryPool',
        'attribute': 'Usage',
    },
]

JOLOKIA_REQUESTS_CMS = JOLOKIA_REQUESTS_BASE + [
    {
        'type': 'read',
        'mbean': 'java.lang:name=Par Eden Space,type=MemoryPool',
        'attribute': 'Usage',
    },
    {
        'type': 'read',
        'mbean': 'java.lang:name=Par Survivor Space,type=MemoryPool',
        'attribute': 'Usage',
    },
    {
        'type': 'read',
        'mbean': 'java.lang:name=CMS Old Gen,type=MemoryPool',
        'attribute': 'Usage',
    },
]

MackerelFormatter.prefix = "jvm8_heap"
MACKEREL_FORMATTERS = {
    'java.lang:name=Eden Space,type=MemoryPool': MackerelHeapFormatter('eden'),
    'java.lang:name=Survivor Space,type=MemoryPool': MackerelHeapFormatter('survivor'),
    'java.lang:name=Tenured Gen,type=MemoryPool': MackerelHeapFormatter('tenured'),
    'java.lang:name=Metaspace,type=MemoryPool': MackerelHeapFormatter('meta'),
    'java.lang:name=Compressed Class Space,type=MemoryPool': MackerelHeapFormatter('ccs'),
    'java.lang:name=Code Cache,type=MemoryPool': MackerelHeapFormatter('code'),
    'HeapMemoryUsage': MackerelHeapFormatter('heap_total'),
    'NonHeapMemoryUsage': MackerelHeapFormatter('nonheap_total'),
    'java.lang:name=PS Eden Space,type=MemoryPool': MackerelHeapFormatter('eden'),
    'java.lang:name=PS Survivor Space,type=MemoryPool': MackerelHeapFormatter('survivor'),
    'java.lang:name=PS Old Gen,type=MemoryPool': MackerelHeapFormatter('tenured'),
    'java.lang:name=Par Eden Space,type=MemoryPool': MackerelHeapFormatter('eden'),
    'java.lang:name=Par Survivor Space,type=MemoryPool': MackerelHeapFormatter('survivor'),
    'java.lang:name=CMS Old Gen,type=MemoryPool': MackerelHeapFormatter('tenured'),
}


if __name__ == '__main__':
    main(sys.argv, MACKEREL_FORMATTERS)