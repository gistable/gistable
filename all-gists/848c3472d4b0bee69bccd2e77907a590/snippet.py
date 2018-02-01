#!/usr/bin/env python
import sys
import pprint


def displayhook_pprint(o):
    """Display hook powered by pprint.

    https://www.python.org/dev/peps/pep-0217/

    """
    if o is None:
        return
    if sys.version_info[0] == 2:
        import __builtin__ as builtins
    else:
        import builtins
    # Set '_' to None to avoid recursion
    # https://docs.python.org/3/library/sys.html#sys.displayhook
    builtins._ = None
    pprint.pprint(o)
    builtins._ = o

sys.displayhook = displayhook_pprint
