import re
from collections import defaultdict

start = re.compile('^\s+')


def avg(fn):
    prev = None
    diffs = []
    for line in open(fn):
        if not line.strip():
            continue
        try:
            L = len(start.findall(line)[0])
        except IndexError:
            L = 0
        if prev is not None:
            diffs.append(abs(prev - L))
        prev = L
    counts = defaultdict(int)
    for diff in diffs:
        if diff == 0:
            continue
        counts[diff] += 1
    counts = sorted(counts.items(), lambda x,y: cmp(y[1], x[1]))
    try:
        most_common = counts[0]
        return most_common[0]
    except IndexError:
        return None

if __name__ == '__main__':
    import sys
    filenames = sys.argv[1:]
    for filename in filenames:
        a = avg(filename)
        if a:
            print a, '\t', filename