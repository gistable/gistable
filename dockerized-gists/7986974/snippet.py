#!/usr/bin/env python

import os
import mmap
import struct
import signal
import optparse
import cql

try:
  import whisper
except ImportError:
  raise SystemExit('[ERROR] Please make sure whisper is installed properly')

# Ignore SIGPIPE
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

option_parser = optparse.OptionParser(usage='''%prog path''')
(options, args) = option_parser.parse_args()

if len(args) != 1:
  option_parser.error("require one input file name")
else:
  path = args[0]

def mmap_file(filename):
  fd = os.open(filename, os.O_RDONLY)
  map = mmap.mmap(fd, os.fstat(fd).st_size, prot=mmap.PROT_READ)
  os.close(fd)
  return map

def read_header(map):
  try:
    (aggregationType,maxRetention,xFilesFactor,archiveCount) = struct.unpack(whisper.metadataFormat,map[:whisper.metadataSize])
  except:
    raise CorruptWhisperFile("Unable to unpack header")

  archives = []
  archiveOffset = whisper.metadataSize

  for i in xrange(archiveCount):
    try:
      (offset, secondsPerPoint, points) = struct.unpack(whisper.archiveInfoFormat, map[archiveOffset:archiveOffset+whisper.archiveInfoSize])
    except:
      raise CorruptWhisperFile("Unable to read archive %d metadata" % i)

    archiveInfo = {
      'offset' : offset,
      'secondsPerPoint' : secondsPerPoint,
      'points' : points,
      'retention' : secondsPerPoint * points,
      'size' : points * whisper.pointSize,
    }
    archives.append(archiveInfo)
    archiveOffset += whisper.archiveInfoSize

  header = {
    'aggregationMethod' : whisper.aggregationTypeToMethod.get(aggregationType, 'average'),
    'maxRetention' : maxRetention,
    'xFilesFactor' : xFilesFactor,
    'archives' : archives,
  }
  return header

def dump_header(header):
  print 'Meta data:'
  print '  aggregation method: %s' % header['aggregationMethod']
  print '  max retention: %d' % header['maxRetention']
  print '  xFilesFactor: %g' % header['xFilesFactor']
  print

def dump_archive_headers(archives):
  for i,archive in enumerate(archives):
    print 'Archive %d info:' % i
    print '  offset: %d' % archive['offset']
    print '  seconds per point: %d' % archive['secondsPerPoint']
    print '  points: %d' % archive['points']
    print '  retention: %d' % archive['retention']
    print '  size: %d' % archive['size']
    print

def dump_archives(archives):
  name = path.replace('/opt/graphite/storage/whisper/','',1)
  name = name.replace('.wsp','',1)
  name = name.replace('/', '.')
  con = cql.connect('127.0.0.1', 9160,  'metric', cql_version='3.0.0')
  print ("Connected to Cassandra!")
  cursor = con.cursor()
  for i,archive in enumerate(archives):
    print 'Archive %d data:' %i
    offset = archive['offset']
    for point in xrange(archive['points']):
      (timestamp, value) = struct.unpack(whisper.pointFormat, map[offset:offset+whisper.pointSize])
      print '%d: %d, %10.35g' % (point, timestamp, value)
      offset += whisper.pointSize
      period = archive['retention']
      rollup = archive['secondsPerPoint']
      ttl = period
      #CQLString = "UPDATE metric USING TTL ? SET data = data + ? WHERE tenant = '' AND rollup = ? AND period = ? AND path = ? AND time = ?;"
      #cursor.execute(CQLString, [ttl, value, rollup, period, name, timestamp])
      #print CQLString, [ttl, value, rollup, period, name, timestamp]
      if timestamp > 0:
        CQLString = "UPDATE metric USING TTL %d SET data = data + [ %d ] WHERE tenant = '' AND rollup = %d AND period = %d AND path = '%s' AND time = %d;" % (ttl, value, rollup, period, name, timestamp)
        #print CQLString
        cursor.execute(CQLString)
    print

if not os.path.exists(path):
  raise SystemExit('[ERROR] File "%s" does not exist!' % path)

map = mmap_file(path)
header = read_header(map)
dump_header(header)
dump_archive_headers(header['archives'])
dump_archives(header['archives'])
