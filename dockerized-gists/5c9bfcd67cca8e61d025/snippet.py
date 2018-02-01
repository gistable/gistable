# fcicq's file counter, 2014.5.19, GPLv3, fcicq at fcicq dot net
import os

def calc_dir_dict(d, basedir, max_dirs=15, max_files=150, max_MBsize=128):
  currdir = basedir
  dir_stack = []
  data = {}
  d_basedir = d[basedir]
  data[basedir] = [d_basedir[1], d_basedir[2], d_basedir[0]] # dirs, files, filesize
  while True:
    # Note: the basedir is already counted
    if d[currdir][3]:
      found = False
      while d[currdir][3]:
        currdir_next = os.path.join(currdir, d[currdir][3][0])
        if currdir_next in d: # it is a must!
          dir_stack.append(d[currdir][3][0])
          found = True
          break
        else:
          d[currdir][3].remove(d[currdir][3][0])
      if found:
        currdir = currdir_next
        continue
    if not dir_stack and not d[currdir][3]:
      break
    # deepest
    dirs, files, filesize = d[currdir][1], d[currdir][2], d[currdir][0]
    if currdir in data:
      dirs += data[currdir][0]
      files += data[currdir][1]
      filesize += data[currdir][2]
    # identify here
    if dirs >= max_dirs:
      print('LargeSubDirs (%d): %s' % (dirs, currdir))
      dirs = -1 # parent handling
    if files >= max_files:
      print('LargeFileNum (%d): %s' % (files, currdir))
      files = 0
    if filesize >= max_MBsize * 1048576:
      print('LargeDirSize (%.2fMB): %s' % (float(filesize) / 1048576.0, currdir))
      filesize = 0
    currdirname = dir_stack.pop()
    currdir = os.path.dirname(currdir)
    d[currdir][3].remove(currdirname)
    # add back to the parent
    if currdir in data:
      data[currdir][0] += dirs
      data[currdir][1] += files
      data[currdir][2] += filesize
    else:
      data[currdir] = [dirs, files, filesize]

def calc_dir(basepath, fsizeMB=10, max_dirs=15, max_files=150, max_MBsize=128, max_suftypes=7, max_smallfiles=20, disable_error=True):
  datadict = {}
  filesize_limit = fsizeMB * 1048576
  if not os.path.isdir(basepath):
    raise Exception('bad path')
  try:
    for root, dirs, files in os.walk(basepath):
      # filesize, dirs, file
      sum_size = 0
      link_dirs = []
      # drop links
      if os.path.islink(root):
        dirs = []
        continue

      # remove links
      for d in dirs:
        d_path = os.path.join(root, d)
        if os.path.islink(d_path):
          dirs.remove(d)

      suffset = set()
      small_files = 0
      for f in files:
        f_path = os.path.join(root, f)
        try:
          f_size = os.path.getsize(f_path)
          if f_size > 0 and f_size <= 32768:
            small_files += 1
        except OSError:
          if not disable_error:
            print('OSError: %s' % f_path)
          f_size = 0
        except KeyboardInterrupt:
          raise
        if filesize_limit and f_size >= filesize_limit:
          print('LargeFile (%.2fMB): %s' % (float(f_size) / 1048576.0, f_path))
        if max_suftypes and f_size:
          f_base, f_ext = os.path.splitext(f)
          if f_base:
            suffset.add(f_ext)
        sum_size += f_size
      if len(suffset) > max_suftypes:
        print('ManySufTypes (%d): %s' % (len(suffset), root))
      if small_files >= max_smallfiles:
        print('ManySmallFil (%d): %s' % (small_files, root))
      datadict[root] = [sum_size, len(dirs), len(files), dirs]
    return calc_dir_dict(datadict, basepath, max_dirs, max_files, max_MBsize)
  except KeyboardInterrupt:
    pass
  return None

if __name__ == '__main__':
  import sys
  if len(sys.argv) == 2:
    calc_dir(sys.argv[1], 0)
  else:
    print('Usage: %s path' % (sys.argv[0]))
