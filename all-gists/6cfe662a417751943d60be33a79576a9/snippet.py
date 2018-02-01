#!/usr/bin/env python2.7

import os
import json
import argparse
import math

def convert_size(size_bytes):
   if (size_bytes == 0):
       return '0B'
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes/p, 2)
   return '%s %s' % (s, size_name[i])

def listProjects(BASE_DIR):
  projects = []
  for group in os.listdir("%s/repositories" % BASE_DIR):
    for project in os.listdir("%s/repositories/%s" % (BASE_DIR, group)):
      projects.append("%s/%s" % (group, project))
  return projects

def listProjectRevisions(BASE_DIR, project):
  return os.listdir("%s/repositories/%s/_manifests/revisions/sha256/" % (BASE_DIR, project))

def listProjectTags(BASE_DIR, project):
  tags = []
  for tag in os.listdir("%s/repositories/%s/_manifests/tags" % (BASE_DIR, project)):
    tagData = { 'name' : tag, 'revs' : [], 'current' : '' }
    for rev in os.listdir("%s/repositories/%s/_manifests/tags/%s/index/sha256" % (BASE_DIR, project, tag)):
      tagData['revs'].append(rev)

    with open("%s/repositories/%s/_manifests/tags/%s/current/link" % (BASE_DIR, project, tag), 'r') as cur:
      tagData['current'] = cur.read().split(':')[1]
    tags.append(tagData)
  return tags

def getRevisionSize(BASE_DIR, revision):
  if not os.path.isfile("%s/blobs/sha256/%s/%s/data" % (BASE_DIR, revision[:2], revision)):
    return 0
  with open("%s/blobs/sha256/%s/%s/data" % (BASE_DIR, revision[:2], revision), 'r') as cur:
    revData = json.load(cur)
    size = 0
    for l in revData['layers']:
      size += l['size']
    size += revData['config']['size']
  return size

BASE_DIR = '/var/opt/gitlab/gitlab-rails/shared/registry/docker/registry/v2/repositories'

print "Existing projects:"
for proj in listProjects(BASE_DIR):
  revs = listProjectRevisions(BASE_DIR, proj)
  tags = listProjectTags(BASE_DIR, proj)
  currentRevs = map(lambda x: x['current'], tags)
  orphanedRevs = filter(lambda x: x not in currentRevs, revs)
  totalSize = 0
  orphanedTotalSize = 0

  for rev in revs:
    revSize = getRevisionSize(BASE_DIR, rev)
    totalSize += revSize
    orphanedTotalSize += revSize if rev not in currentRevs else 0
  print ">> %40s (%d revisions, %-3d orphaned revisions, %-2d tags, %s total size, %s orphans size)" % (
        proj, 
        len(revs), len(orphanedRevs), 
        len(tags), 
        convert_size(totalSize), convert_size(orphanedTotalSize))

