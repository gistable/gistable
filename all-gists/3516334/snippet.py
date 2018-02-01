#
# Python Template Markup Language
# Simple Python DSL for HTML and (a little) CSS templating.
#
# Example:
#
# from ptml import *
#
# with html5 as out:
#   with head:
#     css(href='style.css')
#     title('Hello, world!')
#     with style:
#       p.info(color='red')
#
#   with body:
#     p('Lorem ipsum dolor set amet.')
#     p('Lorem ipsum dolor set amet.')
#
# print(out)
#
# Output:
#
# <!DOCTYPE html>
# <html>
#  <head>
#      <link rel="stylesheet" type="text/css" href="style.css" /><title>Hello, world!</title>
#      <style type="text/css">
#        p.info { color: red; }
#      </style>
#  </head>
#  <body>
#      <p>Lorem ipsum dolor set amet.</p>
#      <p>Lorem ipsum dolor set amet.</p>
#  </body>
# </html>
#
# You can use any HTML tags this way, as well as generate CSS in the same manner.
# Notice CSS and HTML generation is unified, the only difference is CSS declarations
# are put into `with style` blocks. If you put exactly same code into any other
# `with` block, it will be rendered as HTML instead of CSS.
#
# Also, as HTML+CSS is now a normal Python code, implementing layouts and template inheritance
# is as easy, as doing the same things in Python. E.g. layout can be a function like this:
#
# def layout(content):
#   with html5 as c:
#     with head:
#       title(content.title)
#     body(content())
#   return c
#
# And if view is just another function, it can be used as following:
#
# def view():
#   with p as c:
#     _('Lorem ipsum ')
#     i('dolor')
#     _(' set amet.')
#   return c
#
# print(layout(view))
# 
# And of cause, if you don't like pollution of your module scope with a lot of external definitions,
# you can just `import ptml as p` and use all "tags" by prefixing them with `p.` (like `p.html5`).
#

__all__ = []

try:
    from html import escape
except ImportError:
    def escape(text, quote=True):
        for k, v in ('&', '&amp;'), ('<', '&lt;'), ('>', '&gt;'):
            text = text.replace(k, v)

        if quote:
            for k, v in ('"', '&quot;'), ("'", '&#x27;'):
                text = text.replace(k, v)

        return text

function = type(lambda:0)
def render(content):
    unwrapped = content() if isinstance(content, function) else content
    return ''.join(map(render, unwrapped)) if hasattr(unwrapped, '__iter__') \
            and not isinstance(unwrapped, (str, bytes, bytearray)) else str(unwrapped)

def export(obj):
    __all__.append(obj.__name__)
    return obj

def iteratable(value):
    return hasattr(value, '__iter__') and not isinstance(value, (str, bytes, bytearray))

def build_attrs(attrs):
    '''
    >>> build_attrs(dict(a=1,b=2,c_1=3,c_2=['a','b','c']))
    ' c-1="3" a="1" c-2="a b c" b="2"'
    >>> build_attrs({})
    ''
    '''
    return ' ' + ' '.join(
            '%s="%s"' % (
                name.replace("_", "-").strip('-'),
                (lambda v: build_style(v) if isinstance(v, dict) else (' '.join(v) if iteratable(v) else str(v)))(
                    (value() if hasattr(value, '__call__') else value)
                ))
                for (name, value) in attrs.items() if value is not None
            ) if attrs else ''

def build_style(attrs):
    '''
    >>> build_style(dict(background="black", margin_left="2px"))
    'margin-left: 2px; background: black;'
    >>> build_style()
    ''
    '''
    def quote(value):
        value = str(value)
        return "'" + value + "'" if ' ' in value else value

    return ' '.join("%s: %s;" % (name.replace('_', '-'), ', '.join(map(quote, value)) if iteratable(value) else quote(value))
            for (name, value) in attrs.items())


context = []

class TagMeta(type):
    def __enter__(cls):
        self = cls()
        return self.__enter__()

    def __exit__(cls, t, v, bt):
        global context
        self = context[-1]
        self.__exit__(t, v, bt)

    def __getattr__(cls, name):
        if name.startswith('__'): raise AttributeError(name)
        return cls[name.replace('_', '-')]

    def __getitem__(cls, name):
        if name.startswith('__'): raise IndexError(name)
        return cls()[name]

    def _(cls, text):
        return cls()._(text)

    def __str__(cls):
        return str(cls())

class Tag(metaclass=TagMeta):
    name = ''
    attrs = {}
    content = []

    def __init__(self, *content, **attrs):
        self.attrs = self.attrs.copy()
        self.content = self.content[:]

        global context
        if context:
            context[-1](self)

        self(*content, **attrs)

    def __call__(self, *content, **attrs):
        global context
        try:
            ctx = context[-1].content
        except IndexError:
            ctx = []

        # If the tag is placed into content, it should be removed from current context,
        # single tag can be in just one content, otherwise tag duplication can occur.
        self.content.extend(map(lambda t: (ctx.remove(t) or t) if isinstance(t, (Tag, function)) and t in ctx else t, content))
        self.attrs.update(attrs)

        return self

    def __enter__(self):
        global context
        context.append(self)
        return self

    def __exit__(self, t, v, bt):
        global context
        assert context.pop() is self

    def __iadd__(self, data):
        return self.text(data)

    def __str__(self):
        content = render(self.content)
        attrs = build_attrs(self.attrs)
        name = self.name
        return '<%(name)s%(attrs)s>%(content)s</%(name)s>' % locals()

    def __getitem__(self, name):
        if name.startswith('__'): raise IndexError(name)
        self.attrs.setdefault('class', []).append(name)
        return self

    def __getattr__(self, name):
        if name.startswith('__'): raise AttributeError(name)
        return self[name.replace('_', '-')]

    def _(self, text):
        self.content.append(escape(str(text)))
        return self

class EmptyTag(Tag):
    def __str__(self):
        return '<%s%s />' % (self.name, build_attrs(self.attrs))

@export
class comment(Tag):
    def __str__(self):
        return '<!-- %s -->' % render(self.content)

@export
class html(Tag):
    doctype = ''
    name = 'html'

    def __str__(self):
        return ('<!DOCTYPE %s>\n' % self.doctype if self.doctype else '') + super(html, self).__str__()

doctypes = {
        'html5': 'HTML',
        'html4': 'HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd"',
        'html4t': 'HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd"',
        'html4f': 'HTML PUBLIC "-//W3C//DTD HTML 4.01 Frameset//EN" "http://www.w3.org/TR/html4/frameset.dtd"',
        'xhtml': 'html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"',
        'xhtmlt': 'html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"',
        'xhtmlf': 'html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd"',

        # Legacy doctypes, for history and consistency
        'html3': 'HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN"',
        'html2': 'HTML PUBLIC "-//IETF//DTD HTML//EN"',
        }

import sys
sys.setrecursionlimit(2000)
_M = sys.modules[__name__]

for name, doctype in doctypes.items():
    __all__.append(name)
    setattr(_M, name, type(name, (html,), {'doctype': doctype}))

def register_all(tags, parent):
    global _M

    for tag in tags.split():
        __all__.append(tag)
        setattr(_M, tag, type(tag, (parent,), {'name': tag}))


register_all('head body title ' + # Main elements
            'div p ' + # Blocks
            'h1 h2 h3 h4 h5 h6 ' + # Headers
            'u b i s a em strong span font ' + # Inline markup
            'del ins ' + # Annotation
            'ul ol li dd dt dl ' + # Lists
            'article section nav aside ' + # HTML5
            'audio video object embed param ' + # Media
            'fieldset legend button textarea label select option ' + # Forms
            'table thead tbody tr th td caption ' + # Tables
            'blockquote cite q abbr acronym address ' + # Citation, quotes etc
            'code samp pre var kbd dfn ' + # Code
            '', Tag)

register_all('meta link br hr input', EmptyTag)

@export
class script(Tag):
    name = 'script'
    attrs = {'type': 'text/javascript'}

@export
class style(Tag):
    name = 'style'
    attrs = {'type': 'text/css'}

    def __str__(self):
        name = self.name
        attrs = build_attrs(self.attrs)
        content = '\n'.join(map(self.css, self.content))
        return '<%(name)s%(attrs)s>%(content)s</%(name)s>' % locals()

    def css(self, tag, scope=''):

        if not isinstance(tag, Tag):
            return str(tag)

        def condition(tag):

            cond = tag.name
            if 'id' in tag.attrs:
                cond += '#' + tag.attrs['id']

            if 'class' in tag.attrs:
                cond += '.' + '.'.join(tag.attrs['class'])

            return cond

        cond = scope + ' ' + condition(tag)
        attrs = tag.attrs.copy()
        attrs.pop('class', None)
        attrs.pop('id', None)
        style = build_style(attrs)

        result = '%s {\n%s\n}\n' % (cond, style)

        result += ''.join(map(lambda t: self.css(t, cond), tag.content))

        return result

@export
class form(Tag):
    name = 'form'
    attrs = {'method': 'POST'}

@export
class css(link):
    attrs = {'type': 'text/css', 'rel': 'stylesheet'}

@export
class _(Tag):
    name = ''

    def __str__(self):
        return render(self.content)

class Section(Tag):
    def __str__(self):
        name = self.name
        content = render(self.content)
        return '<![%(name)s[%(content)s]]>' % locals()

register_all('CDATA RCDATA IGNORE TEMP', Section)

