#!/usr/bin/env python

# spray.py
#
# Spray a message like from a spray can
#
# Talking to people on IRC? Having a problem getting your message across? Fret
# no longer! All you need to do is spray your message into the channel. People
# will soon see that you are an important person with important things to say.
#
# Copyright 2013, Noah Slater <nslater@apache.org>
#
# Copying and distribution of this file, with or without modification, are
# permitted in any medium without royalty provided the copyright notice and this
# notice are preserved.  This file is offered as-is, without any warranty.

import sys
import random

msg = sys.argv[1]

print "\n".join(
    map(lambda x:
        "".join(
            map(
                lambda y:
                    " " * random.randint(1, 20) + msg,
                [1] * random.randint(2, 4)
            )),
        [1] * random.randint(4, 8)
    )
)
