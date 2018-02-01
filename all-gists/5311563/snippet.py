# vim: set fileencoding=utf8
'''
References
- http://stackoverflow.com/a/1966188
- http://en.wikipedia.org/wiki/Tree_(data_structure)

$ python suggest.py prefix
'''
import sys
import redis

PREFIX = 'trie'
TERMINAL = '+'
r = redis.Redis(db=4)

def add_word(word):
    key = PREFIX + ':'
    pipeline = r.pipeline(True)
    for c in word:
        r.zadd(key, c, ord(c))
        key += c
    r.zadd(key, TERMINAL, 0)
    pipeline.execute()

def suggest(text):
    for c in  r.zrange(PREFIX + ":" + text, 0, -1):
        if c == TERMINAL:
            yield text
        else:
            for t in  suggest(text + c):
                yield t

if __name__ == '__main__':
    for word in suggest(sys.argv[1]):
        print word