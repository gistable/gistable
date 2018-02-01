'''Example of a custom ReST directive in Python docutils'''
import docutils.core
from docutils.nodes import TextElement, Inline
from docutils.parsers.rst import Directive, directives
from docutils.writers.html4css1 import Writer, HTMLTranslator

class foo(Inline, TextElement):
    '''This node class is a no-op -- just a fun way to define some parameters.
    There are lots of base classes to choose from in `docutils.nodes`.

    See examples in `docutils.nodes`
    '''
    pass

class Foo(Directive):
    '''This `Directive` class tells the ReST parser what to do with the text it
    encounters -- parse the input, perhaps, and return a list of node objects.
    Here, usage of a single required argument is shown.

    See examples in docutils.parsers.rst.directives.*
    '''
    required_arguments = 1
    optional_arguments = 0
    has_content = True
    def run(self):
        thenode = foo(text=self.arguments[0])
        return [thenode]

class MyHTMLTranslator(HTMLTranslator):
    '''The `HTMLTranslator` turns nodes into actual source code. There is some
    serious magic here: when parsing nodes, `visit_[name](node)` then
    `depart_[name](node)` are called when a node named `[name]` is
    encountered.

    For details see docutils.writers.html4css1.__init__
    '''
    def __init__(self, document):
        HTMLTranslator.__init__(self, document)
    def visit_foo(self, node):
        # don't start tags; use 
        #     self.starttag(node, tagname, suffix, empty, **attributes)
        # keyword arguments (attributes) are turned into html tag key/value
        # pairs, e.g. `{'style':'background:red'} => 'style="background:red"'`
        self.body.append(self.starttag(node, 'span', '', style='background:red'))
    def depart_foo(self, node):
        self.body.append('</span>')

# register the directive, telling docutils to apply `Foo` when the parser
# encounters a `foo`
directives.register_directive('foo', Foo)

# create a `Writer` and set phasers to `MyHTMLTranslator`
html_writer = Writer()
html_writer.translator_class = MyHTMLTranslator

rest_text = \
'''this is a test
==============

it is only a test

.. foo:: whee
'''

# use the writer to turn some ReST text into a string of HTML
html = docutils.core.publish_string(source=rest_text, writer=html_writer)
print html

# write a webpage (or serve it, or whatever)
with open('test.html', 'w') as f:
    f.write(html)