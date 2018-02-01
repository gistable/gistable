#!/usr/bin/env python
import sys
from collections import defaultdict

def hashtags():
    tags = [w for w in sys.stdin.read().split() if w.startswith('#')]
    freq = defaultdict(int)
    for tag in tags:
        freq[tag] += 1
    return sorted(((v, k) for (k, v) in freq.items()), reverse=True)

if __name__ == '__main__':
    print '\n'.join('%7d %s' % t for t in hashtags())
