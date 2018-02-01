import time
import sys

ms = int(sys.argv[1]) if len(sys.argv) > 1 else 250
words, start = 0, time.time()

print "\n"*2

try:
    for line in sys.stdin:
        for word in line.split():
            sys.stdout.write("\r %-30s" % (word,))
            sys.stdout.flush()
            if any(punct in word for punct in ',.!?;:'):
                time.sleep(0.001 * ms * 2)
            else:
                time.sleep(0.001 * ms)
            words += 1

except KeyboardInterrupt:
    pass

finally:
    secs = int(time.time() - start)
    print
    print ("%d words in %d seconds" % (words, secs))
    if secs:
        print ("%d words/second, %d words/minute" % (words/secs, words*60/secs))
