#!/usr/bin/env python

# in rtorrent.rc:
# method.set_key = event.download.finished,sort_finished,"execute={~/scripts/sort.py,$d.get_hash=}"

import xmlrpclib, os, sys, re, shutil, yaml

log_filepath = os.path.expanduser('~/pysort.log')
log_file = open(log_filepath, "w")

sys.stdout = log_file

def htc(m):
    return chr(int(m.group(1), 16))


def urldecode(url):
    rex = re.compile('%([0-9a-hA-H][0-9a-hA-H])', re.M)
    return rex.sub(htc, url)


print '=== BEGIN ==='

# Load config file
with file("/home/dan/scripts/config.yml", "r") as stream:
    config = yaml.load(stream)

# Set base location
base_location = config['base_location']

# Add default location at score of 30
matches = [[config['default'], 30]]

# Find hash from input
rid = sys.argv[1]
print '     Hash: %s' % rid

# rtorrent xmlrpc
rtorrent = xmlrpclib.ServerProxy('http://127.0.0.1/RPC2')

#load torrent info
label = urldecode(rtorrent.d.get_custom1(rid))
base_path = rtorrent.d.get_base_path(rid)

# sanity check to make sure torrent actually exists
if not os.path.exists(base_path):
    print '%s: Base path doesn\'t exist, quitting' % base_path
    exit()

# outputting some information
(start_dir, start_name) = os.path.split(base_path)
print 'File name: %s' % start_name
print ' File dir: %s' % start_dir
print '    Label: %s' % label

# determine match based on label name
if len(label) != 0:
    matches.append([label.lower().replace(" ", "_"), config['label_score']])

# determine a match based on tracker
trackers = rtorrent.t.multicall(rid, '', 't.get_url=')
find_trackers = re.compile('^https?://(\w+\.)*(\w+\.\w+)(:\d+)?/').search(trackers[0][0])
if find_trackers:
    tracker = find_trackers.group(2)
    print '  Tracker: %s' % tracker
    if tracker in config['trackers']:
        matches.append(config['trackers'][tracker])

print '  Matches: %s' % matches

# test matches in order of score
for match in sorted(matches, key=lambda m: m[1], reverse=True):
    final_dir = os.path.join(base_location, match[0])
    if os.path.exists(final_dir):
        break

final_path = os.path.join(final_dir, start_name)
print '  Move to: %s' % (final_dir)

# some checks based on computer path
if base_path == final_path:
    print '%s: File is already at target location' % start_name
    exit()
if os.path.exists(final_path):
    print '%s: Another file already exists at target location' % start_name
    exit()

# move torrent to new location and inform rtorrent
print 'Moving and telling rtorrent to move %s to %s' % (rid, final_dir)
rtorrent.d.set_directory(rid, final_dir)
shutil.move(base_path, final_dir)
rtorrent.d.resume(rid)
log_file.close()
