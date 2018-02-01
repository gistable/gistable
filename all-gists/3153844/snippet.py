import os
import os.path
import sys

from graphite.render.hashing import ConsistentHashRing

instances = []
unwelcome_instances = []
for arg in sys.argv[1:]:
    unwelcome = False
    if arg.startswith('-'):
        arg = arg[1:]
        unwelcome = True
    instance = tuple(arg.split(':', 2))
    instances.append(instance)
    if unwelcome:
        unwelcome_instances.append(instance)
if 0 == len(instances):
    print('Usage: python whisper-clean.py [-]<address>:<instance>[...]')
    sys.exit(1)

ring = ConsistentHashRing(instances)

for dirname, dirnames, filenames in os.walk('/var/lib/graphite/whisper'):
    for filename in filenames:
        pathname = os.path.join(dirname, filename)
        basename, ext = os.path.splitext(filename)
        if '.wsp' != ext:
            print('skipping %s' % os.path.relpath(pathname,
                                                  '/var/lib/graphite/whisper'))
        if ring.get_node(os.path.relpath(os.path.join(dirname, basename),
                                         '/var/lib/graphite/whisper').
                         replace('/', '.')) in unwelcome_instances:
            print('unlinking %s' % pathname)
            os.unlink(pathname)