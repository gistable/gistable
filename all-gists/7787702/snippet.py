#!/usr/bin/python

import json
import os
import shutil
import subprocess
import re

dockerdir = '/var/lib/docker'
volumesdir = os.path.join(dockerdir, 'volumes')

containers = dict((line, 1) for line in subprocess.check_output('docker ps -a -q -notrunc', shell=True).splitlines())

volumes = os.walk(os.path.join(volumesdir, '.')).next()[1]
for volume in volumes:
  if not re.match('[0-9a-f]{64}', volume):
    print volume + ' is not a valid volume identifier, skipping...'
    continue
  volume_metadata = json.load(open(os.path.join(volumesdir, volume, 'json')))

  container_id = volume_metadata['id']
  if container_id in containers:
    print 'Container ' + container_id[:12] + ' does still exist, not clearing up volume ' + volume
    continue
  print 'Deleting volume ' + volume + ' (container: ' + container_id[:12] + ')'
  volumepath = os.path.join(volumesdir, volume)
  print 'Volumepath: ' + volumepath
  shutil.rmtree(volumepath)
