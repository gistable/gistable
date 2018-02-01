# coding: utf-8

"""
Converts Paradox databases to Python objects or CSV.

You don't need any dependency (except Python) to make this module work.
This module is incomplete but reads most Paradox `.DB` files.
If this module is not fast or complete enough for you, consider using pxview.
"""

from __future__ import division
import csv
from datetime import date, datetime, timedelta
from struct import unpack

try:
    force_text = unicode
except NameError:
    force_text = str


__author__ = 'Bertrand Bordage'
__copyright__ = 'Copyright © 2014 Bertrand Bordage'
__license__ = 'MIT'


field_types = {
    1: 'A',   # string
    2: 'D',   # date
    3: 'S',   # short integer
    4: 'I',   # integer
    5: '$',   # money
    6: 'N',   # number
    9: 'L',   # logical (boolean)
    12: 'M',  # memo
    20: 'T',  # time
    21: '@',  # timestamp
    22: '+',  # autoincrement
}


def unpack_signed(fmt, s, complement):
    v = unpack(fmt, s)[0]
    if v == 0:
        return
    if v < 0:
        return v + complement
    return v - complement


I_COMPLEMENT = 1 << (4*8 - 1)
H_COMPLEMENT = 1 << (2*8 - 1)
B_COMPLEMENT = 1 << (1*8 - 1)


def unpack_i(s):
    return unpack_signed('>i', s, I_COMPLEMENT)


def unpack_h(s):
    return unpack_signed('>h', s, H_COMPLEMENT)


def unpack_b(s):
    return bool(unpack_signed('>b', s, B_COMPLEMENT))


def unpack_d(s):
    return -unpack('>d', s)[0]


def to_date(s):
    ordinal = unpack_i(s)
    if ordinal is None:
        return
    try:
        return date.fromordinal(ordinal)
    except ValueError:
        return


def to_time(s):
    seconds = unpack_i(s)
    if seconds is None:
        return
    seconds //= 1000
    return (datetime.min + timedelta(seconds=seconds)).time()


SECONDS_PER_DAY = 60*60*24


def to_datetime(s):
    seconds = int(unpack_d(s) // 1000)
    ordinal, seconds = divmod(seconds, SECONDS_PER_DAY)
    try:
        d = datetime.fromordinal(ordinal)
        return d + timedelta(seconds=seconds)
    except ValueError:
        return


def decode_data(t, v, input_encoding):
    if t == 'A':
        return v.strip('\x00').decode(input_encoding)
    if t == 'S':
        return unpack_h(v)
    if t == 'L':
        return unpack_b(v)
    if t == 'I':
        return unpack_i(v)
    if t == 'D':
        return to_date(v)
    if t == 'T':
        return to_time(v)
    if t == '@':
        return to_datetime(v)
    if t in ('N', '$'):
        return unpack_d(v)
    if t == 'M':
        return ''  # TODO: handle memos
    if t == '+':
        return unpack_i(v)
    return v


def read(filename, dict_output=False, input_encoding='iso-8859-1'):
    """
    Converts a Paradox .DB file to Python objects.
    """
    db_file = open(filename)
    header = db_file.read(4)
    header_size = unpack('>H', header[2:4])[0]
    db_file.seek(0)
    header = db_file.read(header_size*1024//4)
    block_size = ord(header[5])
    n_fields = ord(header[33])
    parts = header.split(filename.split('/')[-1])
    headers, data = parts
    defs = headers[120:]
    columns = data.strip('\x00').split('\x00')[:n_fields]
    fields = []
    for i, column in enumerate(columns):
        t = field_types[ord(defs[i*2])]
        length = ord(defs[i*2+1])
        fields.append((column, t, length))
    record_size = sum([length for _, _, length in fields])
    blank_record = '\x00' * record_size
    # FIXME: I don't know why, but this is not working without dividing
    #        header size by 4.
    data_offset = header_size*1024//4
    rows = []
    block_index = 0
    previous_record = None
    while True:
        offset = data_offset + block_index * block_size * 1024
        db_file.seek(offset)
        block_header = db_file.read(6)
        offset += 6

        next_block_offset = data_offset + (block_index+1) * block_size * 1024
        while offset + record_size < next_block_offset:
            db_file.seek(offset)
            record = db_file.read(record_size)
            if len(record) < record_size or record == blank_record:
                break
            if record == previous_record:
                offset += record_size
                continue
            previous_record = record
            row = []
            for k, t, size in fields:
                db_file.seek(offset)
                v = db_file.read(size)
                offset += size
                v = decode_data(t, v, input_encoding)
                row.append((k, v))
            rows.append(row)
        
        is_last_block = unpack('>H', block_header[0:2])[0] == 0
        if is_last_block:
            break
        block_index += 1
    if dict_output:
        rows = map(dict, rows)
    return fields, rows


def to_csv(filename, output_filename=None):
    """
    Converts a Paradox .DB to a CSV file.
    """
    fields, data = read(filename)
    fieldnames = [c for c, _, _ in fields]
    if output_filename is None:
        output_filename = filename + '.csv'
    d = csv.DictWriter(open(output_filename, 'w'), fieldnames)
    d.writeheader()
    d.writerows([dict([(k, force_text(v).encode('utf-8')) for k, v in row])
                 for row in data])
