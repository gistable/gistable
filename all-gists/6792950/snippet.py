import re
import sys

states = ('DEFAULT', 'HAVE_FILE')
fl = re.compile('^fl=(.*)')
num = re.compile('^\d+ (\d+)')
state = 0
current_file = ''
inclusive = False

f = file(sys.argv[1], 'r')
d = dict()
for line in f.xreadlines():
    line = line.strip()
    if fl.search(line):
        x = fl.search(line)
        if not 'modman' in x.groups(1)[0]:
            continue
        current_file = x.groups(1)[0]
        current_file = re.sub('.*modman/', '', current_file)
        current_file = current_file.split('/')[0]
        state = 1
        continue
    if state == 1:
        if num.search(line):
            x = num.search(line)
            i = d.get(current_file, 0) + int(x.groups(1)[0])
            d[current_file] = i
            if not inclusive:
                state = 0


x = [(v, k) for k, v in d.items()]
x.sort()
for v, k in x:
    print v, k