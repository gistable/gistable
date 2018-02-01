"""
This file contains code that, when run on Python 2.7.5 or earlier, creates
a string that should not exist: u'\Udeadbeef'. That's a single "character"
that's illegal in Python because it's outside the valid Unicode range.

It then uses it to crash various things in the Python standard library and
corrupt a database.

On Python 3... well, this file is full of syntax errors on Python 3. But
if you were to change the print statements and byte literals and stuff:

* You'd probably see the same bug on Python 3.2.
* On Python 3.3, you'd just get an error making the string on the first line.
* On Python 3.3.3, the error even makes sense.

On narrow builds of Python, u'\Udeadbeef' gets immediately truncated to
u'\ubeef', a totally safe character. (It's a nonsense syllable in
Korean.) For once, narrow Python's half-assed Unicode support has saved you.

The relevant bug is: http://bugs.python.org/issue19279
"""

# Use a bug in the UTF-7 decoder to create a string containing codepoint
# U+DEADBEEF. (Keep in mind that Unicode ends at U+10FFFF.)
deadbeef = '+d,+6t,+vu8-'.decode('utf-7', 'replace')[-1]
print repr(deadbeef)
# outputs u'\Udeadbeef'. That's not a valid string literal.

import codecs
with codecs.open('deadbeef.txt', 'w', encoding='utf-8') as outfile:
    print >> outfile, deadbeef
# writes a non-UTF-8 file

try:
    with codecs.open('deadbeef.txt', encoding='utf-8') as infile:
        print infile.read()
except UnicodeDecodeError:
    print "Boom! Broke your text file."

import re
try:
    re.match(u'[A-%s]' % deadbeef, u'test')
except MemoryError:
    print "Boom! Broke your regular expression."

import sqlite3
db = sqlite3.connect('deadbeef.db')
db.execute(u'CREATE TABLE deadbeef (id integer primary key, value text)')
db.execute(u'INSERT INTO deadbeef (value) VALUES (?)', u'\U0001f602')
db.execute(u'SELECT * FROM deadbeef').fetchall()
# This works fine. I'm just convincing you that SQLite has no problem with
# Unicode itself.

db.execute(u'INSERT INTO deadbeef (value) VALUES (?)', deadbeef)
try:
    db.execute(u'SELECT * FROM deadbeef').fetchall()
except sqlite3.OperationalError:
    print "Boom! Corrupted your database."

# As a bonus, if you run that SQLite query at the IPython prompt, it gets
# a second error trying to print out the error message.
