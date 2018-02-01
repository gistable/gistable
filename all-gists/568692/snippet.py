"""BBEdit UNIX filter that wraps one or more optionally-indented, commented
lines to 79 chars, preserving indentation.

Just select all the lines (in their entirety) the comment spans, and invoke.
Works with #, --, and //-style comments.

For example, this... ::

    # Upping this to 10000 makes it 3x faster. 10000 takes 15.936s. 5000 takes 16.303s.

...becomes this::

    # Upping this to 10000 makes it 3x faster. 10000 takes 15.936s. 5000
    # takes 16.303s.

And this... ::

    'PRIMARY-10/14/2008': None,  # A special Congressional primary to fill a vacancy that occurred on 8/20/08 in the 22th district

...becomes this::

    'PRIMARY-10/14/2008': None,  # A special Congressional primary to fill a
                                 # vacancy that occurred on 8/20/08 in the 22th
                                 # district

"""

import re
from sys import argv
from textwrap import wrap


UNCOMMENT_AND_UNINDENT = re.compile('^ *(# |// |-- )', re.MULTILINE)

text = open(argv[1]).read()
stripped = text.lstrip(' ')  # TODO: instead, strip to the first # that's a comment and save the rest (prepending it later). That'll let us use this for things like `for x in range(1):  # Do stuff and other stuff that wraps around to the next line`
m = UNCOMMENT_AND_UNINDENT.search(stripped)
if m:
    comment_prefix = m.group(1)
    indent = ' ' * (len(text) - len(stripped)) + comment_prefix
    stripped = UNCOMMENT_AND_UNINDENT.sub('', stripped)
    print '\n'.join(wrap(stripped, 79, initial_indent=indent, subsequent_indent=indent)),
else:
    print text
