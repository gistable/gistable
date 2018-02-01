from hashlib import sha256
from sys import argv
for fn in argv[1:]:
    if fn == '-':
        f = sys.stdin
    else:
        f = open(fn, 'rb')
    with f:
        print '%s *%s' % (sha256(f.read()).hexdigest(), fn)
