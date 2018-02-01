#!/usr/bin/env python

import hashlib
from collections import defaultdict
from io import BufferedReader, FileIO

from aribgaiji import GAIJI_MAP

"""
TSファイルから字幕を取り出すスクリプト。
$ captiondumper [-c] <in> <out>
-c : 色指定の制御文字を解釈する
-d : DRCSを解釈する
<in>: 入力 '-'にすると標準入力から読み込む
<out>: 出力 '-'にすると標準出力に書き出す (省略時も同様)

recpt1から現在放送中の番組を読んで適当なファイルに落とす例
$ recpt1 27 1830 - | captiondumper - /path/to/jimaku.txt

録画済みのファイルを読んで標準出力に字幕を書き出す例
$ captiondumper /path/to/recorded.m2t

簡易な実装 (ISO13818-1の仕様のうち、いくつかのパターンを無視している)
ため、パースに失敗するファイルがあるかもしれない。
aribgaiji は https://github.com/murakamiy/epgdump_py/blob/master/aribgaiji.py を利用
"""

class TransportStreamFile(BufferedReader):

    """TSファイル"""

    def __init__(self, path):
        BufferedReader.__init__(self, FileIO(path))

    def __next__(self):
        """次のTSパケットを返す"""
        packet = bytearray(self.read(188))
        if len(packet) != 188:
            raise StopIteration
        return packet

class DRCSString(object):
    """DRCS文字列"""

    images = {
        '8473bbfc8870eb44e2124f36ded70f34': '凜',
        '20c5bf5ad460814c4627fa9abe1b5389': '蜻',
        # 細い開き二重括弧
        'f47249bc346fe4194b933b09571cab7d': '((',
        # 太い開き二重括弧
        '618a99e2a0640543bb18ea8269f78f4b': '((',
        # 細い閉じ二重括弧
        'c6ebb54b066867774f42a247df7a6c1b': '))',
        # 太い閉じ二重括弧
        '094fd4e8b58d5c1f016f6cc695c9c8dd': '))',
        # スマイルプリキュアで使われる曲名表示括弧
        '7bb547a3336fb28775ed4b31ccea2c61': '「',
        '78bea8412561249617d2cf8c624a00a6': '」',
        # 疑問符感嘆符 QUESTION EXCLAMATION MARK (U+2048)
        '60bd03df9faa250e0f797d719df1320c': '⁈',
        # 携帯電話 (TBS) MOBILE PHONE (U+1F4F1)
        '9c0ac7f2b2f81acb81b9000e7d8ff56a': '📱',
        # 携帯電話 (CX) MOBILE PHONE (U+1F4F1)
        'd27350b838145fe4433102121e2ba56b': '📱',
        # トランシーバー MOBILE PHONE (U+1F4F1)
        '881edb7f0adc96d25b056f016d2ddd86': '📱',
        # スピーカー1 PUBLIC ADDRESS LOUDSPEAKER (U+1F4E2)
        'b0f1dabe3e27571f654b4196aa7f27e7': '📢',
        # スピーカー2 PUBLIC ADDRESS LOUDSPEAKER (U+1F4E2)
        '24c1bf547f713a666ed983852a8f2fbb': '📢',
        # コンピューター PERSONAL COMPUTER (U+1F4BB)
        '19ec594cff4ebf2f56e5fd1799f89142': '💻',
    }

    def __init__(self, bitmap, depth, width, height):
        self.bitmap = bitmap
        self.md5hash = hashlib.md5(str(bitmap).encode('UTF-8')).hexdigest()
        self.depth = depth
        self.width = width
        self.height = height

    def image(self):
        result = []
        for i in range(0, self.height * 2, 2):
            char = (self.bitmap[i] << 8) | self.bitmap[i+1]
            result.append(format(char, ' 16b').replace('0', ' ').replace('1', '■'))
        return '\n'.join(result)

    def detail(self):
        image = self.image()
        return "{}\n{}".format(image, self.md5hash)

    def __str__(self):
        return self.images.get(self.md5hash, self.detail())

class CProfileString(object):
    """CProfile文字列"""
    mapping = {
        0: ' ',
        7: '\a',
        12: '\n',
        13: '\n',
        32: ' ',
    }

    drcs = {}

    def __new__(cls, data, options):
        if options.color:
            cls.mapping.update({
                0x80: '\033[30m',
                0x81: '\033[31m',
                0x82: '\033[32m',
                0x83: '\033[33m',
                0x84: '\033[34m',
                0x85: '\033[35m',
                0x86: '\033[36m',
                0x87: '\033[37m',
            })
        return object.__new__(cls)

    def __init__(self, data, options):
        self.data = data

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.character())

    def character(self):
        """一文字ずつUnicode型として返すジェネレータ"""
        while self.data:
            char1 = self.data.pop(0)
            if 0xa0 < char1 < 0xff:
                char2 = self.data.pop(0)
                try:
                    yield bytes((char1, char2)).decode('euc-jp')
                except UnicodeDecodeError:
                    gaiji = ((char1 & 0x7f) << 8) | (char2 & 0x7f)
                    if gaiji == 0x7c21:
                        # 次の字幕パケットへセリフが続いていることを示す矢印
                        continue
                    try:
                        yield GAIJI_MAP[gaiji]
                    except KeyError:
                        yield '(0x{:x}{:x})'.format(char1, char2)
            elif options.drcs and 0x20 < char1 < 0x2f:
                yield str(self.drcs.get(char1, '(0x{:x})'.format(char1)))
            elif char1 in self.mapping:
                yield self.mapping[char1]

    def __str__(self):
        return ''.join(self)

def get_packet(ts, target_pids):
    """指定のPIDのTSテーブルを返すジェネレータ

    ts  -- 取得対象のTSファイル
    target_pids  -- 取得対象のPIDのリスト

    """
    buf = defaultdict(bytearray)
    for packet in ts:
        payload_unit_start_indicator = (packet[1] & 0x40) >> 6
        pid = ((packet[1] & 0x1F) << 8) | packet[2]
        has_adaptation = (packet[3] & 0x20) >> 5
        has_payload = (packet[3] & 0x10) >> 4
        if pid in target_pids:
            payload_index = 4
            if has_adaptation:
                adaptation_field_length = packet[payload_index]
                payload_index += adaptation_field_length + 1
            if has_payload:
                if payload_unit_start_indicator:
                    if buf[pid]:
                        yield buf[pid]
                        del buf[pid]
                    if packet[payload_index:payload_index+3] != b'\x00\x00\x01':
                        pointer_field = packet[payload_index]
                        payload_index += pointer_field + 1
                buf[pid].extend(packet[payload_index:])

def get_program_map_PIDs(ts):
    """PATからPMTのIDを返すジェネレータ"""
    packet = next(get_packet(ts, [0x00]))
    table_id = packet[0]
    section_length = ((packet[1] & 0x0F) << 8) | packet[2]
    map_index = 8
    crc_index = section_length - 4
    while map_index < crc_index:
        program_number = (packet[map_index] << 8) | packet[map_index+1]
        program_map_PID = ((packet[map_index+2] & 0x1F) << 8
                          ) | packet[map_index+3]
        map_index += 4
        if program_number != 0:
            yield program_map_PID

def get_caption_pid(packets):
    """PMTから字幕パケットのPIDを返す"""
    for packet in packets:
        table_id = packet[0]
        section_length = ((packet[1] & 0x0F) << 8) | packet[2]
        program_number = (packet[3] << 8) | packet[4]
        program_info_length = ((packet[10] & 0x0F) << 8) | packet[11]
        map_index = 12 + program_info_length
        crc_index = section_length - 4
        while map_index < crc_index:
            stream_type = packet[map_index]
            elementary_PID = ((packet[map_index+1] & 0x1F) << 8
                             ) | packet[map_index+2]
            ES_info_length = ((packet[map_index+3] & 0x0F) << 8
                             ) | packet[map_index+4]
            last = map_index + 5 + ES_info_length
            descriptors = parse_descriptor(packet[map_index+5:last])
            map_index = last
            if (stream_type == 0x06 and 0x52 in descriptors and
                    descriptors[0x52][0][2] == 0x87):
                return elementary_PID

def parse_caption(packet, options):
    """字幕パケットから字幕本文を返すジェネレータ"""
    PES_header_data_length = packet[8]
    PTS = (((packet[9] & 0x0E) << 29) |
           (packet[10] << 22) | ((packet[11] & 0xFE) << 14) |
           (packet[12] << 7) | ((packet[13] & 0xFE) >> 1))
    PES_data_packet_header_length = packet[11 + PES_header_data_length] & 0x0F
    index = 12 + PES_header_data_length + PES_data_packet_header_length
    data_group_id = (packet[index] & 0xFC) >> 2
    data_group_size = (packet[index+3] << 8) | packet[index+4]
    if data_group_id in (0x00, 0x20):
        num_languages = packet[index+6]
        index += 7 + num_languages * 5
    else:
        index += 6
    data_unit_loop_length = ((packet[index] << 16) | packet[index+1] << 8
                            ) | packet[index+2]
    loop_index = 0
    while loop_index < data_unit_loop_length:
        data_unit_parameter = packet[index+4+loop_index]
        data_unit_size = ((packet[index+5+loop_index] << 16
                          ) | packet[index+6+loop_index] << 8
                         ) | packet[index+7+loop_index]
        last = index + 8 + loop_index + data_unit_size
        #print(format(data_unit_parameter, 'X'))
        if data_unit_parameter == 0x20:
            data_unit_data = packet[index+8+loop_index:last]
            a(data_unit_data)
            yield data_unit_data
        elif options.drcs and data_unit_parameter == 0x30:
            data_unit_data = packet[index+8+loop_index:last]
            i = 0
            for _ in range(data_unit_data[0]):
                character_code_1 = data_unit_data[i+1]
                character_code_2 = data_unit_data[i+2]
                num_font = data_unit_data[i+3]
                font_id = (data_unit_data[i+4] & 0xF0) >> 4
                mode = data_unit_data[i+4] & 0x0F
                if mode == 0 or mode == 1:
                    depth = data_unit_data[i+5]
                    width = data_unit_data[i+6]
                    height = data_unit_data[i+7]
                    bitmap = data_unit_data[i+8:i + 8 + height * 2]
                    CProfileString.drcs[character_code_2] = DRCSString(
                        bitmap, depth, width, height)
                    i += 7 + height * 2

        loop_index += data_unit_size + 5

def a(packet):
    """
    for p in packet:
        print(format(p, '02X'), end=' ')
    print()
    """

def parse_descriptor(packet):
    """記述子を必要最低限にパースし、タグID-記述子リストの辞書として返す"""
    total_length = len(packet)
    index = 0
    result = defaultdict(list)
    while index < total_length:
        tag = packet[index]
        length = packet[index+1]
        last = index + length + 2
        result[tag].append(packet[index:last])
        index = last
    return result


if __name__ == '__main__':
    import sys
    from optparse import OptionParser


    parser = OptionParser('usage: %prog [option] [in] [out]')
    parser.add_option('-c', '--color', action='store_true',
                      dest='color', default=False,
                      help='color mode')
    parser.add_option('-d', '--drcs', action='store_true',
                      dest='drcs', default=False,
                      help='display DRCS image to stdout')
    options, args = parser.parse_args()
    try:
        inpath = args[0]
        outpath = args[1] if len(args) > 2 else '-'
    except IndexError:
        sys.exit(parser.print_help())

    path = sys.stdin.fileno() if inpath == '-' else inpath
    out = sys.stdout if outpath == '-' else open(outpath, 'w')
    with TransportStreamFile(path) as ts:
        pmt_pids = list(get_program_map_PIDs(ts))
        caption_pid = [get_caption_pid(get_packet(ts, pmt_pids))]
        for pes in get_packet(ts, caption_pid):
            for caption in parse_caption(pes, options):
                out.write(str(CProfileString(caption, options)))
                out.flush()
