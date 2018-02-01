#!/usr/bin/env python

import binascii
import re
import subprocess
import sys
from os.path import basename

XRANDR_BIN = 'xrandr'

# re.RegexObject: expected format of xrandr's EDID ascii representation
EDID_DATA_PATTERN = re.compile(r'^\t\t[0-9a-f]{32}$')


def get_edid_for_connector(connector_name):
    """Finds the EDID for the given connector.

    Args:
        connector_name (str): Name of a connector, i.e. HDMI-0, DP-1

    Returns:
        Binary EDID for the connector, or None if not found.

    Raises:
        OSError: Failed to run xrandr.
    """

    # re.RegexObject: pattern for this connector's xrandr --props section
    connector_pattern = re.compile('^{} connected'.format(connector_name))

    try:
        xrandr_output = subprocess.check_output([XRANDR_BIN, '--props'])
    except OSError as e:
        sys.stderr.write('Failed to run {}\n'.format(XRANDR_BIN))
        raise e

    output_lines = xrandr_output.decode('ascii').split('\n')

    def slurp_edid_string(line_num):
        """Helper for getting the EDID from a line match in xrandr output."""
        edid = ''
        assert re.match(r'\tEDID:', output_lines[line_num+2])
        for i in range(line_num + 3, len(output_lines)):
            line = output_lines[i]
            if EDID_DATA_PATTERN.match(line):
                edid += line.strip()
            else:
                break
        return edid if len(edid) > 0 else None

    for i in range(len(output_lines)):
        connector_match = connector_pattern.match(output_lines[i])
        if connector_match:
            edid_str = slurp_edid_string(i)
            if edid_str is None:
                return None
            return binascii.unhexlify(edid_str)

    return None


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage: {} <OUTPUT>'.format(basename(sys.argv[0])))

    connector_name = sys.argv[1]

    edid_bin = get_edid_for_connector(connector_name)
    if edid_bin is None:
        sys.exit('No EDID found for output {}'.format(connector_name))

    if sys.version_info >= (3, 0):
        sys.stdout.buffer.write(edid_bin)
    else:
        sys.stdout.write(edid_bin)

    sys.exit(0)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4