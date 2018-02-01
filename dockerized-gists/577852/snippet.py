# autocomplete.py - Redis autocomplete example
# download female-names.txt from http://antirez.com/misc/female-names.txt
# Ruby original: http://gist.github.com/574044

# Requires http://github.com/andymccurdy/redis-py/

from redis import Redis

r = Redis()
KEY = 'compl'

# Create the completion sorted set
if not r.exists(KEY):
    print "Loading entries in the Redis DB"
    for line in open('female-names.txt').readlines():
        line = line.strip()
        for end_index in range(1, len(line)):
            prefix = line[0:end_index]
            r.zadd(KEY, prefix, 0)
        r.zadd(KEY, line + '*', 0)
else:
    print "NOT loading entries, there is already a %s key" % KEY

def complete(r, prefix, count):
    results = []
    rangelen = 50
    start = r.zrank(KEY, prefix)
    if not start:
        return []
    while len(results) != count:
        range = r.zrange(KEY, start, start + rangelen - 1)
        start += rangelen
        if not range or len(range) == 0:
            break
        for entry in range:
            minlen = min((len(entry), len(prefix)))
            if entry[0:minlen] != prefix[0:minlen]:
                count = len(results)
                break
            if entry[-1] == '*' and len(results) != count:
                results.append(entry[0:-1])
    return results

# Complete the string "marcell"
for result in complete(r, "marcell", 50):
    print result