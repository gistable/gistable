"""Display Theano functions in the IPython notebook with pydotprint."""

__author__ = "David Warde-Farley"
__copyright__ = "Copyright 2012, Universite de Montreal"
__credits__ = ["David Warde-Farley"]
__license__ = "3-clause BSD"
__email__ = "wardefar@iro"
__maintainer__ = "David Warde-Farley"


import os
import tempfile
from theano.compile.function_module import Function
from theano.printing import pydotprint

_loaded = False


def print_function_png(o):
    handle, fn = tempfile.mkstemp(suffix='.png')
    try:
        os.close(handle)
        pydotprint(o, outfile=fn, format='png', print_output_file=False)
        with open(fn) as f:
            return f.read()
    finally:
        os.remove(fn)


def load_ipython_extension(ip):
    global _loaded
    if not _loaded:
        png_formatter = ip.display_formatter.formatters['image/png']
        png_formatter.for_type(Function, print_function_png)
        _loaded = True