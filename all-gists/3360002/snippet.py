__all__ = []

def export(value):
    __all__.append(value.__name__)
    return value

import sys
module = sys.modules[__name__]

class Context(object):
    level = 0
    indent = '  '

    def __enter__(self):
        self.level += 1
        return self.__lshift__

    def __exit__(self, type_, value, btrace):
        self.level -= 1

    def __lshift__(self, data):
        print(self.indent * self.level + str(data))
        return self

class StrContext(Context):
    data = ''

    def __lshift__(self, data):
        self.data += self.indent * self.level + str(data) + "\n"
        return self

    def __str__(self):
        return self.data

context = StrContext()
__all__.append('context')

def build_attrs(attrs):
    return ' ' + ' '.join(
            '%s="%s"' % (
                name.replace("_", "-").strip('-'),
                (lambda v: ' '.join(v) if hasattr(v, '__iter__') else v)(
                    (value() if hasattr(value, '__call__') else value)
                ))
                for (name, value) in attrs.iteritems() if value is not None
            ) if attrs else ''

@export
def css(**attrs):
    return ' '.join("%s: %s;" % (name.replace('_', '-'), value)
            for (name, value) in attrs.iteritems())

class TAG(object):
    name = ''
    attrs = {}

    class __metaclass__(type):
        def __enter__(cls):
            return cls().__enter__()

        def __exit__(cls, type_, value, btrace):
            context.level -= 1
            context << '</%s>' % cls.name

        def __getattr__(cls, name):
            return cls[name.replace('_', '-')]

        def __getitem__(cls, name):
            self = cls()
            self.attrs['class'] = [name]
            return self

    def __enter__(self):
        context << '<%s%s>' % (self.name, build_attrs(self.attrs))
        context.level += 1
        return context

    def __exit__(self, type_, value, btrace):
        context.level -= 1
        context << '</%s>' % self.name

    def __call__(self, _content=None, **attrs):
        if attrs:
            self.attrs.update(attrs)

        if _content is not None:
            context << '<%s%s>%s</%s>' % (self.name, build_attrs(self.attrs), _content, self.name)

        return self

    def __init__(self, _content=None, **attrs):
        self.attrs = self.attrs.copy()
        self(_content, **attrs)

    def __getattr__(self, name):
        return self[name.replace('_', '-')]

    def __getitem__(self, name):
        self.attrs.setdefault('class', []).append(name)
        return self

class EMPTYTAG(object):
    name = ''
    attrs = {}

    def __new__(cls, **attrs):
        if attrs:
            _attrs = cls.attrs.copy()
            _attrs.update(attrs)
        else:
            _attrs = cls.attrs

        context << '<%s%s />' % (cls.name, build_attrs(_attrs))

@export
class COMMENT(TAG):
    def __enter__(self):
        context << '<!-- '
        return context

    def __exit__(self, type_, value, traceback):
        context << ' -->'

@export
class HTML(TAG):
    name = 'html'
    doctype = ''

    def __enter__(self):
        context << '''<!DOCTYPE %s>''' % (self.doctype)
        return super(HTML, self).__enter__()

@export
class HTML5(HTML):
    doctype = 'HTML'

simple_tags = ('head body title ' + # Main elements
            'div p blockquote ' + # Blocks
            'h1 h2 h3 h4 h5 h6 ' + # Headers
            'u b i s a em strong span font ' + # Inline markup
            'del ins ' + # Annotation
            'ul ol li dd dt dl ' + # Lists
            'article section nav aside ' + # HTML5
            'audio video object embed param ' + # Media
            'fieldset legend button textarea label select option ' + # Forms
            'table thead tbody tr th td caption ' + # Tables
            ''
            )
empty_tags = 'meta link br hr input'

for tag in simple_tags.split():
    name = tag.upper()
    __all__.append(name)
    setattr(module, name, type(name, (TAG,), {'name': tag}))

for tag in empty_tags.split():
    name = tag.upper()
    __all__.append(name)
    setattr(module, name, type(name, (EMPTYTAG,), {'name': tag}))

@export
class SCRIPT(TAG):
    name = 'script'
    attrs = {'type': 'text/javascript'}

@export
class CSS(LINK):
    attrs = {'type': 'text/css', 'rel': 'stylesheet'}

    def __new__(cls, href):
        super(CSS, cls).__new__(cls, href=href)

@export
class JS(SCRIPT):
    def __init__(self, src):
        super(JS, self).__init__('', src=src)

@export
class FORM(TAG):
    name = 'form'
    attrs = {'method': 'POST'}

    def __init__(self, action='', **attrs):
        super(FORM, self).__init__(action=action, **attrs)
