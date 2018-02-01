import os
import re

SPLITTER = re.compile(r'\n(?=[^\s])', re.MULTILINE)

def files(path):
  for root, dirs, files in os.walk(path):
      for f in files:
          if f.endswith('.txt') or f.endswith('.robot') or f.endswith('.tsv'):
              yield os.path.join(root, f)

def parts(filename, minimum_rows_in_block):
    with open(filename, 'r') as f:
        for part in SPLITTER.split(f.read().lower()):
            if part.count('\n') > minimum_rows_in_block:
                name, data = part.split('\n', 1)
                yield '%s:%s' % (filename, name), data


def find_duplications(path, minimum_rows_in_block):
    sames = {}
    for f in files(path):
        for n, d in parts(f, minimum_rows_in_block):
            if d not in sames:
               sames[d] = set()
            sames[d].add(n)
    return sames

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print 'python duplicator.py [DIRECTORY TO GO THROUGH]'
        sys.exit(0)
    sames = find_duplications(sys.argv[1], 5)
    for k in sames:
        if len(sames[k]) > 1:
            print '='*80
            for name in sames[k]:
                print 'path:',name
            print 'total number of duplicates', len(sames[k])
            print '-'*80
            print k
            print '-'*80

