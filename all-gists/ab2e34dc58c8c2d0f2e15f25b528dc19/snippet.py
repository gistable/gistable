#! /usr/bin/env python-pyrocore

from pyrocore import connect
import os

files = {}

verbose = False
test = False

rootDir = "/home/username/torrents/rtorrent"
minSize = 1048576 # 1 mb of data before trying to map file
minSizeConflicts = 1e8 # 0.1 Gb of data min to not skip conflict


conflictItems = 0
conflictBytes = 0
totalItems = 0
totalBytes = 0

for dirName, subdirList, fileList in os.walk(rootDir):
    for fname in fileList:
        file = dirName + '/' + fname
        size = os.path.getsize(file)

        totalItems += 1
        totalBytes += size

        if size < minSize:
          pass

        elif files.has_key(size) and size < minSizeConflicts:
          print('Warning: we have two files with the same size (%s)' % str(size))
          print('  %s' % file)
          print('  %s' % files[size])
          print('Skipping file...')

          files[size] = '__CONFLICT__'

          conflictItems += 1
          conflictBytes += size

        else:
          files[size] = file

        if files.has_key(fname):
          print('Warning: we have two files with the same name (%s)' % fname)
          print(' %s' % file)
          print(' %s' % files[fname])
          print('Skipping file...')

          files[fname] = '__CONFLICT__'

        else:
          files[fname] = file



print('{0} files treated, of which {1} have been skipped due to size conflicts'.format(totalItems, conflictItems))
print('It represents about {0} bytes of data to be re-downloaded'.format(conflictBytes))

rt = connect()
proxy = rt.open()

torrents = proxy.download_list()
print('Treating torrents')
for hash in torrents:
  name = proxy.d.get_name(hash)
  multi = proxy.d.is_multi_file(hash)

  # exists = os.path.exists(dir)
  # print('  %s (%s %s)' % (name, dir, u'\033[92m\u2713\033[0m' if exists else u'\033[91m\u2717\033[0m'))
  # last =  os.path.basename(os.path.dirname(dir))

  newPath = '/home/username/torrents/rtorrent/Bulk/' + name if multi == 1 else ''

  fileCount = proxy.d.size_files(hash)

  if verbose: print('    ' + str(fileCount) + ' files detected')

  print('d.set_directory_base ' + newPath)

  if not test:
    proxy.d.set_directory_base(hash, newPath)

  for i in xrange(0, fileCount):
    id = hash + ':f' + str(i)

    fileName = proxy.f.get_path(id)
    fileSize = proxy.f.get_size_bytes(id)

    base = os.path.basename(fileName)

    if verbose: print('     %s (%s)' % (fileName, str(fileSize)))

    size = False
    name = False

    size = files.has_key(fileSize) and files[fileSize] != '__CONFLICT__'

    name = files.has_key(base) and files[base] != '__CONFLICT__'

    identifier = fileSize if size else fileName

    if name and not size:
      fileSize2 = os.path.getsize(files[base])
      size = fileSize2 == fileSize

    if size or (size and name) :
      # Let's go!

      target = newPath + '/' + fileName

      try:
        os.makedirs(os.path.dirname(target))
      except OSError as exc:
        pass

      try:
        source = files[identifier]
        print(source + ' <= ' + target)

        if not test:
          os.link(source, target)

      except KeyError as exc:
        pass
      except OSError as exc:
        pass
      except UnicodeDecodeError as exc:
        pass