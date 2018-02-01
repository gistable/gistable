# -*- coding: utf-8 -*-
"""
    pygments.formatters.htmlline
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Formatter for HTML output which wraps each line in a span.

"""

__all__ = ['HtmlLineFormatter']

from pygments.formatters import HtmlFormatter

class HtmlLineFormatter(HtmlFormatter):
    """
    Output as html and wrap each line in a span
    """
    name = 'Html wrap lines'
    aliases = ['htmlline']

    def wrap(self, source, outfile):
        return self._wrap_div(self._wrap_pre(self._wrap_lines(source)))

    def _wrap_lines(self, source):
        i = self.linenostart
        for t, line in source:
            if t == 1:
                line = '<span id="LC%d">%s</span>' % (i, line)
                i += 1
            yield t, line