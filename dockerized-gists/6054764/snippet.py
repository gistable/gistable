import sys
import time


if __name__ == '__main__':
    begin = time.time()
    l = sys.stdin.readline()
    while l:
        sys.stdout.write("%f %s" % (time.time() - begin, l))
        l = sys.stdin.readline()