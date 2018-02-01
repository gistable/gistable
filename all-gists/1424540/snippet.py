#! /usr/bin/env python
import fileinput
import argparse
from operator import itemgetter

parser = argparse.ArgumentParser()
parser.add_argument('--target-mb', action = 'store', dest = 'target_mb', default = 61000, type = int)
parser.add_argument('vmtouch_output_file', action = 'store', nargs = '+')
args = parser.parse_args()

entries = []
last_fl_name = None
for line in open(args.vmtouch_output_file[0]):
    line = line.strip()
    if line.startswith('['):
        # this is a mem info row
        if not last_fl_name:
            continue
        currently_paged_percent = line.rsplit(' ', 1)[-1]
        num, denom = map(float, currently_paged_percent.split('/'))
        if num and denom:
            bytes = denom * 4096
            mb = bytes / (1024 * 1024)
            entries.append((last_fl_name, num / denom, mb))
    elif line.startswith('.') or line.startswith('/'):
        last_fl_name = line

sorted_entries = sorted(entries, key = itemgetter(1), reverse = True)
loaded_mb = 0

to_page_in = []
for entry in sorted_entries:
    if loaded_mb <= args.target_mb:
        loaded_mb += entry[-1]
        to_page_in.append(entry[0])

print 'vmtouch -m 5G -vt', ' '.join(to_page_in)
