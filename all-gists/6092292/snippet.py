# Helper script to turn a single monolithic WHISPER_DIR into one that is
# allocated based on the shard id (carbon-cache instance name)
#
# Take a single WHISPER_DIR such as '/opt/graphite/storage/whisper' and
# figure out how to divide them up into shards based on the given list of
# carbon-cache shard instances and replication_factor
#
# The output will be multiple text files that can be used with `rsync --files-from=`
# to copy the right .wsp files to the correct nodes.
#
# example usage:
#
#   $ PYTHONPATH=/opt/graphite/lib/ python whisper-shard.py
#
#       Beginning scan of: /opt/graphite/storage/whisper
#
#       Finished scan. Writing file lists ...
#
#        Saving file list: 16.files ...
#        Saving file list: 10.files ...
#        Saving file list: 05.files ...
#        Saving file list: 08.files ...
#        Saving file list: 20.files ...
#        Saving file list: 09.files ...
#        Saving file list: 27.files ...
#        Saving file list: 29.files ...
#        Saving file list: 13.files ...
#        Saving file list: 23.files ...
#        Saving file list: 07.files ...
#        Saving file list: 31.files ...
#        Saving file list: 15.files ...
#        Saving file list: 12.files ...
#        Saving file list: 24.files ...
#        Saving file list: 11.files ...
#        Saving file list: 25.files ...
#        Saving file list: 17.files ...
#        Saving file list: 28.files ...
#        Saving file list: 22.files ...
#        Saving file list: 14.files ...
#        Saving file list: 18.files ...
#        Saving file list: 26.files ...
#        Saving file list: 06.files ...
#        Saving file list: 30.files ...
#        Saving file list: 01.files ...
#        Saving file list: 21.files ...
#        Saving file list: 02.files ...
#        Saving file list: 03.files ...
#        Saving file list: 32.files ...
#        Saving file list: 19.files ...
#        Saving file list: 04.files ...
#
# After the file lists are created, rsync the *.wsp files to the correct directory
# on the correct nodes.
#
#   $ rsync -r --files-from=01.files /opt/graphite/storage/whisper/ vnode-01:/opt/graphite/storage/whisper/01/
#   $ rsync --r -files-from=02.files /opt/graphite/storage/whisper/ vnode-02:/opt/graphite/storage/whisper/02/
#    ... etc ...
#
# Or, some bash magic to simplify the process:
#
#   $ for i in {01..32}; do rsync -r --files-from=$i.files /opt/graphite/storage/whisper/ vnode-$i:/opt/graphite/storage/whisper/$i/ ; done
#

import os
import os.path

from carbon.routers import ConsistentHashingRouter


DEBUG = False


# 32 shards, 01-32.
REPLICATION_FACTOR = 2
WHISPER_PATH = '/opt/graphite/storage/whisper'
DESTINATIONS = [
    "vnode-01:3001:01", "vnode-02:3002:02", "vnode-03:3003:03", "vnode-04:3004:04",
    "vnode-05:3005:05", "vnode-06:3006:06", "vnode-07:3007:07", "vnode-08:3008:08",
    "vnode-09:3009:09", "vnode-10:3010:10", "vnode-11:3011:11", "vnode-12:3012:12",
    "vnode-13:3013:13", "vnode-14:3014:14", "vnode-15:3015:15", "vnode-16:3016:16",
    "vnode-17:3017:17", "vnode-18:3018:18", "vnode-19:3019:19", "vnode-20:3020:20",
    "vnode-21:3021:21", "vnode-22:3022:22", "vnode-23:3023:23", "vnode-24:3024:24",
    "vnode-25:3025:25", "vnode-26:3026:26", "vnode-27:3027:27", "vnode-28:3028:28",
    "vnode-29:3029:29", "vnode-30:3030:30", "vnode-31:3031:31", "vnode-32:3032:32"
]

# use the ConsistentHashingRouter from carbon-relay
router = ConsistentHashingRouter(replication_factor=REPLICATION_FACTOR)
for dest in DESTINATIONS:
    router.addDestination(dest.split(':'))

file_map = {}
count = 0

print "Beginning scan of: %s" % WHISPER_PATH
for dirname, dirnames, filenames in os.walk(WHISPER_PATH):
    for filename in filenames:
        pathname = os.path.join(dirname, filename)
        rel_pathname = os.path.relpath(pathname, WHISPER_PATH)
        basename, ext = os.path.splitext(filename)
        if '.wsp' != ext:
            print('skipping %s' % pathname)

        # convert filesystem path to metric style path. remove WHISPER_DIR prefix, then
        # convert / to .
        rel_path = os.path.relpath(os.path.join(dirname, basename), WHISPER_PATH)
        metric_path = rel_path.replace('/', '.')

        dests = [d for d in router.getDestinations(metric_path)]
        for d in dests:
            if d not in file_map:
                file_map[d] = []
            file_map[d].append(rel_pathname)  # relative pathname for rsync --files-from
        if DEBUG:
            print "%s\t%s" % (dests, pathname)

print "Finished scan. Writing file lists ...\n"

for shard, files in file_map.items():
    shard_id = shard[2]  # ('vnode-30', '3130', '30')
    file_name = '%s.files' % shard_id  # 30.files

    print "Saving file list: %s ..." % file_name
    with open(file_name, 'w') as f:
        for path in files:
            f.write('%s\n' % path)
