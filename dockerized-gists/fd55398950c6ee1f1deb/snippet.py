#!/usr/bin/env python
"""How to do regular expressions in sqlite3 (using python)."""
from __future__ import print_function

import re
import sys
import time
import datetime
import sqlite3


def words():
    with open('/usr/share/dict/words', 'rb') as fp:
        for word in fp:
            yield word.strip()


def main(argv=sys.argv):
    def regexp(y, x, search=re.search):
        return 1 if search(y, x) else 0

    con = sqlite3.connect(":memory:")

    con.create_function('regexp', 2, regexp)

    con.execute('CREATE TABLE words (word text);')

    wordtuple = tuple(words())

    con.executemany('INSERT INTO words VALUES(?)', zip(wordtuple))

    start = datetime.datetime.now()
    for row in con.execute('SELECT * FROM words WHERE word REGEXP ?', [r'(?i)xylo']):
        print(row)
    end = datetime.datetime.now()
    print(start)
    print(end)

    start = datetime.datetime.now()
    for val in filter(lambda w: re.search(r'(?i)xylo', w), wordtuple):
        print(val)
    end = datetime.datetime.now()

    print(start)
    print(end)


if __name__ == '__main__':
    main()
