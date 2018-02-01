#!/usr/bin/python2
from __future__ import print_function
from docopt import docopt
from neovim import attach
from neovim.api import NvimError
import os
import sys
__doc__ = """nvim-command - Run a command in the running neovim session.
Usage:
    nvim-command <command>..."""
if __name__ == "__main__":
    nvim = None
    try:
        nvim = attach("socket", path=os.environ["NVIM_LISTEN_ADDRESS"])
    except KeyError:
        print("No neovim session found.", file=sys.stderr)
        sys.exit(1)
    try:
        nvim.command(" ".join(docopt(__doc__)["<command>"]))
    except NvimError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
