# -*- encoding: utf-8 -*-
#
# Copyright © 2016 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import struct

import bitarray


def double_to_int(f):
    """Convert a 64 bits float to a 64 bits integer."""
    return struct.unpack("!Q", struct.pack("!d", f))[0]


def int_to_double(i):
    """Convert an integer to a 64 bits float."""
    return struct.unpack("!d", struct.pack("!Q", i))[0]


def to_binary64(v):
    """Convert value to a binary representation on 64 bits as a string."""
    return "{:064b}".format(v)


def count_lead_and_trail_zeroes(d):
    """Count the number of leading and trailing zeroes in an integer."""
    as_str = "{:64b}".format(d)
    try:
        leading_zeroes = as_str.index("1")
        trailing_zeroes = 63 - as_str.rindex("1")
    except ValueError:
        return 64, 64
    return leading_zeroes, trailing_zeroes


def encode_xor_floats(floats):
    """Encode a list of floats using XOR encoding.

    Encoding stolen from paper:
         "Gorilla: A Fast, Scalable, In-Memory Time Series Database"
    """
    if len(floats) == 0:
        return b""
    prev = double_to_int(floats[0])
    encoded = bitarray.bitarray(to_binary64(prev))
    prev_lz = prev_tz = 0
    for v in floats[1:]:
        v = double_to_int(v)
        xor = prev ^ v
        if xor == 0:
            encoded.append(0)
        else:
            encoded.append(1)

            lz, tz = count_lead_and_trail_zeroes(xor)

            if lz >= 32:
                lz = 31

            if prev_lz != 0 and lz >= prev_lz and tz >= prev_tz:
                encoded.append(0)
                encoded.extend(
                    to_binary64(xor >> prev_tz)[- (64 - prev_lz - prev_tz):])
            else:
                prev_lz = lz
                prev_tz = tz
                encoded.append(1)
                encoded.extend(to_binary64(lz)[-5:])
                sigbits = 64 - lz - tz
                encoded.extend(to_binary64(sigbits)[-6:])
                encoded.extend(to_binary64(xor >> tz)[-sigbits:])
        prev = v

    return encoded.tobytes()

_ARRAY_3_ZERO = bitarray.bitarray('000')
_ARRAY_2_ZERO = bitarray.bitarray('00')


def decode_xor_floats(encoded, number_of_values):
    if number_of_values == 0:
        return []

    array = bitarray.bitarray()
    array.frombytes(encoded.tobytes())

    results = []
    # Read first value
    results.append(struct.unpack("!d", array[:64].tobytes())[0])

    index = 64

    for _ in range(number_of_values - 1):
        index += 1
        if array[index - 1]:
            index += 1
            if array[index - 1]:
                bits = _ARRAY_3_ZERO + array[index:index + 5]
                leading = struct.unpack("!B", bits.tobytes())[0]
                bits = _ARRAY_2_ZERO + array[index + 5:index + 11]
                trailing = 64 - leading - struct.unpack(
                    "!B", bits.tobytes())[0]
                index += 11
            sigbits = 64 - leading - trailing
            bits = bitarray.bitarray(
                '0' * (64 - sigbits)) + array[index:index + sigbits]
            num = struct.unpack("!Q", bits.tobytes())[0]
            index += sigbits

            vbits = double_to_int(results[-1])
            vbits ^= num << trailing
            results.append(int_to_double(vbits))
        else:
            results.append(results[-1])
    return results
