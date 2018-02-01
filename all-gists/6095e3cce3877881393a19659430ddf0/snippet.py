#!/usr/bin/env python

from __future__ import print_function

import base64
import ctypes
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from urllib.parse import urlencode


def main():
    tree = ET.parse(sys.argv[1])
    root = tree.getroot()
    assert root.tag == 'map'

    for child in root:
        assert child.tag == 'string'
        name = child.attrib['name']
        if name == 'tokenOrder':
            continue

        if ':' in name:
            service, user = name.split(':', 1)
        else:
            user = name
            service = 'Unknown'

        info = json.loads(child.text)
        #print("Info for %s: %r" % (name, info))

        # Ensure that we only have unsigned values, then get secret
        secret_bytes = [ctypes.c_ubyte(x).value for x in info['secret']]
        secret_hex = ''.join('%02X' % (x,) for x in secret_bytes)
        secret = bytes.fromhex(secret_hex)
        secret_b32 = base64.b32encode(secret)

        # Make fancy URL.
        params = {
            'secret': secret_b32,
            'issuer': service,
            'counter': info['counter'],
            'digits': info['digits'],
            'period': info['period'],
            'algorithm': info['algo'],
        }

        tmpl = 'otpauth://{type}/{service}:{user}?{params}'
        url = tmpl.format(
            type=info['type'].lower(),
            service=service,
            user=user,
            params=urlencode(params),
        )
        #print(url)

        print("Displaying: {0}".format(name))
        process_qrencode = subprocess.Popen(['qrencode', '-o', '-', url],
                                            stdout=subprocess.PIPE)
        process_display = subprocess.Popen(['display'],
                                           stdin=process_qrencode.stdout)

        # Allow the qrencode to recieve a SIGPIPE if display exits
        process_qrencode.stdout.close()
        process_display.communicate()


if __name__ == "__main__":
    main()