#!/usr/bin/python3
"""
Export your Windows Bluetooth LE keys into Linux!

Thanks to: http://console.systems/2014/09/how-to-pair-low-energy-le-bluetooth.html

Usage:

$ ./export-ble-infos.py <args>
$ sudo bash -c 'cp -r ./bluetooth /var/lib && service bluetooth force-reload'
$ rm -r bluetooth
"""

import os
import shutil
import subprocess
import sys
import tempfile

from configparser import ConfigParser
from optparse import OptionParser

default_template = """
[General]
Name=Designer Mouse
Appearance=0x03c2
AddressType=static
SupportedTechnologies=LE;
Trusted=true
Blocked=false
Services=00001800-0000-1000-8000-00805f9b34fb;00001801-0000-1000-8000-00805f9b34fb;0000180a-0000-1000-8000-00805f9b34fb;0000180f-0000-1000-8000-00805f9b34fb;00001812-0000-1000-8000-00805f9b34fb;

[IdentityResolvingKey]
Key=

[LocalSignatureKey]
Key=
Counter=0
Authenticated=false

[LongTermKey]
Key=
Authenticated=0
EncSize=16
EDiv=
Rand=

[DeviceID]
Source=2
Vendor=1118
Product=2053
Version=272

[ConnectionParameters]
MinInterval=6
MaxInterval=6
Latency=60
Timeout=300
"""


def main():
    parser = OptionParser()
    parser.add_option("-v", "--verbose", action='store_true', dest='verbose')
    parser.add_option("-s", "--system", dest="system", metavar="FILE",
                      default="/media/mygod/Windows/Windows/System32/config/system",
                      help="SYSTEM file in Windows. Usually at /Windows/System32/config/system.")
    parser.add_option("-k", "--key", dest="key", metavar="KEY",
                      default=r"ControlSet001\Services\BTHPORT\Parameters\Keys",
                      help="Registry key for BT. [default: %default]")
    parser.add_option("-o", "--output", dest="output", metavar="DIR", default="bluetooth",
                      help="Output directory. [default: %default]")
    parser.add_option("-t", "--template", dest="template", metavar="FILE", help="Template file.")
    parser.add_option("-a", "--attributes", dest='attributes', help="Additional attributes file to be copied.")
    options, args = parser.parse_args()

    if options.template:
        with open(options.template) as file:
            template = file.read()
    else:
        template = default_template

    out = tempfile.mktemp(".reg")
    reged = subprocess.Popen(["reged", "-x", options.system, '\\', options.key, out], stdout=sys.stderr)
    reged.wait()
    if reged.returncode:
        return reged.returncode
    dump = ConfigParser()
    with open(out) as file:
        reged_out = file.read()
        if options.verbose:
            print(reged_out)
        dump.read_string(reged_out.split('\n', 1)[1])
    os.unlink(out)

    for section in dump:
        path = section[len(options.key) + 2:].split('\\')
        assert not path[0]
        if len(path) == 3:
            path[1] = ':'.join([path[1][i:i + 2] for i in range(0, len(path[1]), 2)]).upper()
            path[2] = ':'.join([path[2][i:i + 2] for i in range(0, len(path[2]), 2)]).upper()
            print("Dumping {}/{}...".format(path[1], path[2]))
            config = ConfigParser()
            config.optionxform = str
            config.read_string(template)

            def read_reg(key, expected_type):
                def read_reg_actual(key, expected_type):
                    actual_type, content = dump[section]['"{}"'.format(key)].split(':', 1)
                    if expected_type == 'hex16':
                        assert actual_type == 'hex'
                        content = content.split(',')
                        assert len(content) == 16
                        return ''.join(content).upper()
                    if expected_type == 'qword':
                        assert actual_type == 'hex(b)'
                        content = content.split(',')
                        assert len(content) == 8
                        return str(int(''.join(content[::-1]), 16))
                    if expected_type == 'dword':
                        assert actual_type == expected_type
                        return str(int(content, 16))
                    assert False
                result = read_reg_actual(key, expected_type)
                if options.verbose:
                    print("{} of type {}: {}".format(key, expected_type, result))
                return result
            config['LongTermKey']['Key'] = read_reg('LTK', 'hex16')
            # KeyLength ignored for now
            config['LongTermKey']['Rand'] = read_reg('ERand', 'qword')
            config['LongTermKey']['EDiv'] = read_reg('EDIV', 'dword')
            config['IdentityResolvingKey']['Key'] = read_reg('IRK', 'hex16')
            config['LocalSignatureKey']['Key'] = read_reg('CSRK', 'hex16')
            output_dir = os.path.join(options.output, path[1], path[2])
            os.makedirs(output_dir, exist_ok=True)
            with open(os.path.join(output_dir, 'info'), 'w') as file:
                config.write(file, False)
            if options.attributes:
                shutil.copyfile(options.attributes, os.path.join(output_dir, 'attributes'))


if __name__ == "__main__":
    sys.exit(main())
