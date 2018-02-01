#!/usr/bin/python
"""
Reads EAC log, generates musicbrainz disc TOC listing for use as discid.
Opens browser with discid query on musicbrainz.org.

Warning: may work wrong for discs having data tracks. May generate wrong results on other non-standard cases.
"""

import re
import sys
import webbrowser

class NotSupportedTOCError(Exception):
    pass

def filter_toc_entries(lines):
    """
    Take iterator of lines, return iterator of toc entries
    """
    while True:
        line = lines.next()
        # to allow internationalized EAC output where column headings
        # may differ
        if re.match(r""" \s* 
                   .+\s+ \| (?#track)
                \s+.+\s+ \| (?#start)
                \s+.+\s+ \| (?#length)
                \s+.+\s+ \| (?#start sec)
                \s+.+\s*$   (?#end sec)
                """, line, re.X):
            lines.next()
            break

    while True:
        line = lines.next()
        m = re.match(r"""
            ^\s*
            (?P<num>\d+)
            \s*\|\s*
            (?P<start_time>[0-9:.]+)
            \s*\|\s*
            (?P<length_time>[0-9:.]+)
            \s*\|\s*
            (?P<start_sector>\d+)
            \s*\|\s*
            (?P<end_sector>\d+)
            \s*$
            """, line, re.X)
        if not m:
            break
        yield m.groupdict()

def calculate_mb_toc_numbers(eac_entries):
    """
    Take iterator of toc entries, return list of numbers for musicbrainz disc id
    """
    eac = list(eac_entries)
    num_tracks = len(eac)
    
    tracknums = [int(e['num']) for e in eac]
    if range(1,num_tracks+1) != tracknums:
        raise NotSupportedTOCError("Non-standard track number sequence: %s", tracknums)
    
    leadout_offset = int(eac[-1]['end_sector']) + 150 + 1
    offsets = [(int(x['start_sector']) + 150) for x in eac]
    return [1, num_tracks, leadout_offset] + offsets
    
f = open(sys.argv[1])
#conv = (line.decode(sys.argv[2]) for line in f)
mb_toc_urlpart = "%20".join(str(x) for x in calculate_mb_toc_numbers(filter_toc_entries(f)))

webbrowser.open("http://musicbrainz.org/bare/cdlookup.html?toc=%s" % mb_toc_urlpart)