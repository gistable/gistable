from functools import partial
from operator import concat
from os.path import isfile

from fold import foldl


def _list_files_from(part, prev):
    current = "%s/%s" % (prev, part)
    if isfile(current):
        return [current]
    else:
        ls = partial(_list_files_from, prev=current)
        return foldl([], concat, map(ls, listdir(current)))

def list_files_from(start):
  return _list_files_from(start, ".")
