#! /usr/bin/env python

"""{escher} -- one-file key-value storage.

What?
  This is a toy application to manage persistent key-value string data.
  The file {escher} is *both* the application and its data.
  When you run any of the commands below, the file will be executed and,
  after data change, it will rewrite itself with updated data.
  You can copy the file with whatever name to create multiple datasets.
  Remember that the data will be copied with the file. Each file must
  be readable, writable, and executable.

Why?
  I don't know; this is probably useless.

Usage:
  Listing current keys:
  $ {escher}

  Getting the value of the foo key:
  $ {escher} foo
  (NOTE: If foo is not in the dataset, exit code will be 1.)

  Setting the value of foo to bar:
  $ {escher} foo bar

  Removing the key foo:
  $ {escher} foo ""
  (NOTE: If foo is not in the dataset, exit code will be 1.)

  Removing everything:
  $ {escher} --clean

  Printing this help message:
  $ {escher} --help
"""

from __future__ import print_function

import sys
import os
import pickle
import zlib
import base64

__doc__ = __doc__.format(escher=os.path.basename(__file__))

sep = "--//--"

f = open(__file__, "r")
esc, her = f.read().split(repr(sep), 1)
f.close()

data = pickle.loads(zlib.decompress(base64.b64decode(her[1:].strip())))

args = sys.argv[1:]
print([
  lambda            : "\n".join(sorted(data.keys())) if data else
                      sys.exit(),
  lambda key        : __doc__ if key == "--help" else
                      not data.clear() and "X *" if key == "--clean" else
                      data.get(key, False) or
                      sys.exit("Error: key not found."),
  lambda key, value : not data.update([(key, value)]) and
                      " ".join([key, "<-", value]) if value else
                      data.pop(key, True) and "X " + key if key in data else
                      sys.exit("Error: key not found."),
  lambda fu, ti, le : print("Error: invalid argument list.") or sys.exit(2)
][min(len(args), 3)](*args[:3]))

her = base64.b64encode(zlib.compress(pickle.dumps(data, 2))).decode('ascii')

out = repr(sep).join([esc, "\n#" + her + "\n"])
with open(__file__, "w") as f: f.write(out)

'--//--'
#eJxrYKotZNADAAaFAZ8=
