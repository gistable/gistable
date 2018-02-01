"""
An IPython magic function to pretty-print objects with syntax highlighting.

See, "Defining your own magics":
http://ipython.org/ipython-doc/stable/interactive/reference.html#defining-your-own-magics

For more on Pygments:
http://pygments.org/docs/quickstart/

Usage
-----

Place this file in your IPython startup directory. The default location is::

    ~/.ipython/profile_default/startup/

NOTE for Django: Since django uses an embedded IPython shell, it may not
load your default IPython profile. You'll need to run:

    %run /path/to/this/file


License
-------

Copyright (c) 2014, Brad Montgomery <brad@bradmontgomery.net>

Released under the MIT License.
http://opensource.org/licenses/MIT

"""
from __future__ import print_function

from IPython.core.magic import Magics, magics_class, line_magic
from pprint import pformat
from pygments import highlight
from pygments.formatters import Terminal256Formatter  # Or TerminalFormatter
from pygments.lexers import PythonLexer


@magics_class
class PrettyColorfulInspector(Magics):
    """Implementation for a magic function that inpects a given python object,
    and then prints a syntax-highlighted and pretty-printed version of it."""

    @line_magic
    def inspect(self, line):
        if line:
            # evaluate the line to get a python object
            python_object = self.shell.ev(line)

            # Pretty Print/Format the object
            formatted_object = pformat(python_object)

            # Use Pygments to do syntax highlighting
            lexer = PythonLexer()
            formatter = Terminal256Formatter()
            output = highlight(formatted_object, lexer, formatter)

            # Print the output, but don't return anything (othewise, we'd
            # potentially get a wall of color-coded text.
            print(output)


# Register with IPython
ip = get_ipython()
ip.register_magics(PrettyColorfulInspector)