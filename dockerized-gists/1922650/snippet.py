# -*- coding: utf-8 -*-
import sys
from pprint import PrettyPrinter


class UnicodePrettyPrinter(PrettyPrinter):
    """Unicode-friendly PrettyPrinter

    Prints:
      - u'привет' instead of u'\u043f\u0440\u0438\u0432\u0435\u0442'
      - 'привет' instead of '\xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82'

    """
    def format(self, *args, **kwargs):
        repr, readable, recursive = PrettyPrinter.format(self, *args, **kwargs)
        if repr:
            if repr[0] in ('"', "'"):
                repr = repr.decode('string_escape')
            elif repr[0:2] in ("u'", 'u"'):
                repr = repr.decode('unicode_escape').encode(sys.stdout.encoding)
        return repr, readable, recursive

    def _repr(self, object, context, level):
        repr, readable, recursive = self.format(object, context.copy(),
                                                self._depth, level)
        if not readable:
            self._readable = False
        if recursive:
            self._recursive = True
        return repr


def upprint(obj, stream=None, indent=1, width=180, depth=None):
    printer = UnicodePrettyPrinter(stream=stream, indent=indent, width=width, depth=depth)
    printer.pprint(obj)

def upformat(obj, stream=None, indent=1, width=180, depth=None):
    printer = UnicodePrettyPrinter(stream=stream, indent=indent, width=width, depth=depth)
    printer.pformat(obj)
