"""
IPython magics for displaying source code files with syntax highlighting.
This uses the Pygments library: http://pygments.org.

Two magics are available:

%highlight: This uses a terminal formatter and will work in any of IPython's
    front ends.

%highlight_html: This uses an HTML formatter and is best used in the
    IPython Notebook. This gives access to all available Pygments styles.

"""
from __future__ import print_function

import uuid

from pygments import highlight
from pygments.lexers import get_lexer_by_name, get_lexer_for_filename
from pygments.formatters import HtmlFormatter, TerminalFormatter

from IPython.utils.ipstruct import Struct
from IPython.core.magic import Magics, magics_class, line_magic
from IPython.display import display, HTML

HTML_TEMPLATE = """<style>
{}
</style>
{}
"""


@magics_class
class PygmentsMagic(Magics):
    def __init__(self, shell):
        super(PygmentsMagic, self).__init__(shell)

    @line_magic
    def highlight(self, parameter_s=''):
        """
        Display the contents of a source code file with syntax highlighting.

        Requires the pygments library.

        Usage:
            %highlight [options] <file name>

        Options:

            -g {'dark', 'light'}: Specify the 'dark' or 'light' color scheme.
                Defaults to 'dark'.

            -l <lexer name>: Manually specify the language of the code using
                any lexer name from http://pygments.org/docs/lexers/.
                By default the source language is guessed from the file name.

        """
        opts_def = Struct(l='', g='dark')
        opts, arg_str = self.parse_options(parameter_s, 'l:g:')
        opts.merge(opts_def)

        if opts.l:
            lexer = get_lexer_by_name(opts.l)
        else:
            lexer = get_lexer_for_filename(arg_str)

        formatter = TerminalFormatter(bg=opts.g)

        with open(arg_str) as f:
            code = f.read()

        print(highlight(code, lexer, formatter))

    @line_magic
    def highlight_html(self, parameter_s=''):
        """
        Display the contents of a source code file with syntax highlighting.

        You must be in an environment that can display HTML output.
        Requires the pygments library.

        Usage:
            %highlight [options] <file name>

        Options:

            -n: Show line numbers.

            -s <style name>: An available Pygments style, default is 'default'.

            -l <lexer name>: Manually specify the language of the code using
                any lexer name from http://pygments.org/docs/lexers/.
                By default the source language is guessed from the file name.

        """
        opts_def = Struct(l='', s='default')
        opts, arg_str = self.parse_options(parameter_s, 'l:s:n')
        opts.merge(opts_def)

        if opts.l:
            lexer = get_lexer_by_name(opts.l)
        else:
            lexer = get_lexer_for_filename(arg_str)

        if 'n' in opts:
            linenos = 'table'
        else:
            linenos = False

        formatter = HtmlFormatter(style=opts.s,
                                  cssclass='pygments' + str(uuid.uuid4()),
                                  linenos=linenos)

        with open(arg_str) as f:
            code = f.read()

        html_code = highlight(code, lexer, formatter)
        css = formatter.get_style_defs()

        html = HTML_TEMPLATE.format(css, html_code)

        display(HTML(html))


def load_ipython_extension(ipython):
    ipython.register_magics(PygmentsMagic)
