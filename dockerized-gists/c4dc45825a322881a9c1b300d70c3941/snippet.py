"""
An implementation of TOTP as described in https://tools.ietf.org/html/rfc6238#section-4 aka Google Authenticator Style 2-factor Auth
"""
import base64
import datetime
import hashlib
import hmac
import sys
import struct
import time

from tqdm import tqdm

key_b32 = raw_input('Enter the secret (base32)')
key = base64.b32decode(key_b32.strip().upper())

# The time interval (TI) which defines the size of the chunks
T_INTERVAL = 30
def unixtime():
    return int(time.time())

def code(now):
    # TC is the the time chunk that we're a part of
    time_chunk = int(now / T_INTERVAL)

    # Per the spec, the time is represented as an 8-byte string in
    # big endian. >q == big endian unsigned long
    time_bytes = struct.pack('>q', time_chunk)
    # The default hmac algorithm is md5!
    hm = hmac.new(key, time_bytes, hashlib.sha1)
    hex_digest = hm.hexdigest()

    assert len(hex_digest) == 40

    # Take the last 4 bits. These become the offset into the array
    offset = int(hex_digest[-1:], 16)

    # Take 4 bytes starting from the offset (in bytes). Our array is half-bytes
    relevant_bytes = int(hex_digest[offset*2:offset*2+8], 16)

    # Drop the highest order bit to work around platform issues
    masked = relevant_bytes & 0x7FFFFFFF

    num_digits = 6

    final = masked % (10 ** num_digits)
    final_str = str(final).zfill(6)
    return final_str

if raw_input('Your current code is {}. Would you like a vanity code? y/n\n'.format(code(unixtime()))) == 'n':
    sys.exit(0)

goal = raw_input('What do you want your two factor code to be?')
assert len(goal) == 6
start = unixtime()
num_tried = 0
# probably need to try about 1 million
pbar = tqdm(total=1000000)
while code(start) != goal:
    pbar.update(1)
    start += 30

pbar.close()

print('Your vanity 2-factor code will be available on: ')
print(
    datetime.datetime.fromtimestamp(
       start
    ).strftime('%Y-%m-%d %H:%M:%S')
)



