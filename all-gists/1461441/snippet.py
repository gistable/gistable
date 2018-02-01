"""
A really stupid python template language inspired by coffeekup, markaby.
Do not use this code, it will ruin your day.  A byproduct of insomnia.

TL;DR
-----

This module defines a template language that allows us to do:

    d = Doc()
    with d.html:

        with d.head:
            d.title ('example page')
            d.link  (rel='stylesheet', href='/style.css', type='text/css')

        with d.body (style='foo'):
            d.a ('other stuff on another page', href='/other.html')
            d.p ('stuff on this page')


Motivation
----------

Python templating has always been a problem for me.  You normally have to
write in your target language (i.e. HTML) with some horrible syntax for
inlining python.  For example, this is a Cheetah [1] template:

    <html>
      <head><title>$title</title></head>
      <body>
        <table>
          #for $client in $clients
          <tr>
            <td>$client.surname, $client.firstname</td>
            <td><a href="mailto:$client.email">$client.email</a></td>
          </tr>
          #end for
        </table>
      </body>
    </html>

We have '$' and '#' to inline python code and variables.  This to me is the
wrong way round.  I want to write python and not html.  I do not want to manage
html braces.  Tavis Rudd has pointed out that many of the arguments for
non python templates are unfounded [2] and I agree with him.  This has been
further enforced for me by using haml [3] and coffeekup [4], which leaves us in the
ridiculous position that the best indent based templating DSLs for html are in
non indent based languages (ruby, javascript).

This is why we can't have nice things
-------------------------------------

Coffescript and ruby have some advantage over python for a DSL including the
way anonymous blocks are defined and the ability to omit brackets and still get
function execution.  This means that the most direct python templates, such as
lxml builder[5] and breve [6] end up with a nested structure.  For example,
this is an lxml template:

    html = E.HTML(
          E.HEAD(
            E.LINK(rel="stylesheet", href="great.css", type="text/css"),
            E.TITLE("Best Page Ever")
          ),
          E.BODY(
            E.H1(E.CLASS("heading"), "Top News"),
            E.P("World News only on this page", style="font-size: 200%"),
            "Ah, and here's some more text, by the way.",
            lxml.html.fromstring("<p>    and this is a parsed fragment    </p>")
          )
        )

Now, this code is python, but logic expressed this way still requires
management of parens and is not indent based - so is not really 'pythonic'.
It also cannot really use conditionals and loops beyond ternarys and list comprehensions.
So I wondered if we could hook up a bit of magic using some other method.
So which way to go?  Function definitions would require too much magic, so it
seems that the best way is the _with_ statement.

The result is the style shown in the TL;DR above.  We can also
wrap this in a template method to use python conditional logic based
on supplied data:

    def example_template(items):
        d = Doc()
        with d.html:

            with d.head:
                d.title ('other stuff on this page')
                d.link  (rel='stylesheet', href='/style.css', type='text/css')

            with d.body (style='foo'):
                d.a ('other stuff on another page', href='/other.html')
                d.p ('stuff on this page')
                with d.ul:
                    for i in items:
                        with d.li:
                            d.a (str(i), href=str(i) + '.html')
        return d.to_string()

The code below also shows template inheritance from python classes.

This is currently based on the lxml builder, and so it is slightly slower
than the elementree benchmarks [7] (which is pretty slow).  The lazy decorator
that allows us to miss out brackets on with statements is probably going
to make you cry.  Still this seems like a reasonable template language in
about 40 lines of code.

[1] http://www.cheetahtemplate.org/examples.html
[2] https://bitbucket.org/tavisrudd/throw-out-your-templates/src/98c5afba7f35/throw_out_your_templates.py
[3] http://haml-lang.com/
[4] http://coffeekup.org/
[5] http://lxml.de/dev/api/lxml.builder.ElementMaker-class.html
[6] http://breve.twisty-industries.com/
[7] http://spitfire.googlecode.com/svn/trunk/tests/perf/bigtable.py

Comments, abuse, etc to twitter @casualbon or casbon (at) gmail.com
"""
import lxml
import lxml.html
import lxml.html.builder
import lxml.etree

class TagContext(object):
    """ The context manager for an HTML tag """

    __slots__ = ['doc', 'node', 'tag']

    def __init__(self, tag, doc, *content, **props):
        """ create an html tag belonging to doc with given content and properties"""
        self.doc = doc
        self.tag = tag

    def __call__(self, *content, **props):
        text = ''
        for c in content:
            if len(c) and c[0] == '#':
                props['id'] = c[1:]
            elif len(c) and c[0] == '.':
                props['class'] = c[1:]
            else:
                text += c

        text += props.get('text', '')

        self.node = getattr(lxml.html.builder, self.tag.upper())(**props)
        if self.doc.stack:
            self.doc.stack[-1].append(self.node)

        if content:
            self.node.text = text

        self.doc.tail_node = self.node
        return self

    def __enter__(self):
        """ entering the node appends it to the document stack """
        self.doc.stack.append(self.node)
        self.doc.tail_node = None

    def __exit__(self, t, v, tb):
        """ exiting the node pops it from the stack """
        if len(self.doc.stack) > 1:
            self.doc.stack.pop()
        self.doc.tail_node = self.node

    def each(self, iterable):
        for i in iterable:
            with self():
                yield self, i

    def set(self, key, value):
        self.node.set(key, value)


class Lazydec(object):
    """ Horrible decorator to allow the with statement to omit
        brackets by tracking if context returned by doc has been entered
    """

    __slots__ = ['x']

    def __init__(self, x):
        self.x = x

    def __call__(self, *args, **kws):
        return self.x(*args, **kws)

    def __enter__(self):
        if self.x.__name__ == 'tagcallable':
            self.x = self.x()
        return self.x.__enter__()

    def __exit__(self, *args):
        return self.x.__exit__(*args)



class Doc(object):
    """ A document manages a stack, the head of which is the current context node """

    Context = TagContext

    def __init__(self, *args, **kws):
        self.stack = []
        self.tail_node = None # this node is set if text needs to be put in its tail

    def __getattr__(self, name):
        """ Override getattr for quick tag access

            This means Doc.html returns a tag
        """
        return self.Context(name, self)

    def text(self, text):
        """ append raw text """
        if self.tail_node is not None:
            self.tail_node.tail = (self.tail_node.tail or '') + text
        else:
            self.stack[-1].text = (self.stack[-1].text or '') + text

    def fragment(self, html):
        """ append a html fragment (must be a single element) """
        try:
            self.stack[-1].append(lxml.html.fragment_fromstring(html))
        except lxml.etree.ParserError:
            els = lxml.html.fragments_fromstring(html)
            for e in els:
                self.stack[-1].append(e)

    def to_string(self, pretty_print=True):
        """ convert this document to string """
        return lxml.html.tostring(self.stack[0],
                pretty_print=pretty_print,
                doctype='<!DOCTYPE html>')




class BootstrapContext(TagContext):

    def _add_class(self, props, cls):
        if 'class' not in props:
            props['class'] = cls
        else:
            props['class'] = props['class'] +  ' ' + cls

    def __call__(self, *content, **props):

        # support span and offset
        for gridcls in ['span', 'offset']:
            if gridcls in props:
                self._add_class(props, gridcls + str(props[gridcls]))
                props.pop(gridcls)

        return TagContext.__call__(self, *content, **props)


class Bootstrap(Doc):
    Context = BootstrapContext



if __name__ == '__main__':

    def example_template(items):
        """ template function example"""

        d = Doc()
        p = d.html()
        print p.__class__
        with d.html():
            d.fragment('<h1>no tail</h1>')

            with d.head():
                d.title ('other stuff on this page')
                d.link  (rel='stylesheet', href='/style.css', type='text/css')

            with d.body (style='foo'):
                d.a ('other stuff on another page', href='/other.html')
                d.p ('stuff on this page')
                with d.ul():
                    for i in items:
                        with d.li():

                            d.a (str(i), href=str(i) + '.html')

                d.text('hi')
                d.div('.foo', '#bar', 'inside el')
                d.text('bye')
            return d.to_string()


    class BaseTemplate(object):
        """ template inheritance example """

        title = 'base'

        def render(self):
            d = Doc()
            with d.html():

                with d.head():
                    d.title (self.title)
                    d.link  (rel='stylesheet', href='/style.css', type='text/css')

                with d.body (style='foo'):
                    with d.div ('#header'):
                        self.header(d)
                    with d.div ('#content'):
                        self.content(d)
                    with d.div ('#footer'):
                        self.footer(d)

            return d.to_string()

        def header(self, d):
            pass

        def content(self, d):
            pass

        def footer(self, d):
            d.span('Never read this content')


    class ItemTemplate(BaseTemplate):

        title = 'item view'

        def __init__(self, items):
            self.items = items

        def header(self, d):
            d.p('view of %s items' % len(self.items))

        def content(self, d):
            with d.ul():
                for li, i in d.li.each(self.items):
                    li.set('id', str(i))
                    d.text('the cake is a li')
                    d.a (str(i), href=str(i) + '.html')

    def bootstrap_example():
        d = Bootstrap()
        with d.html():
            d.div('#main', span=8, offset=3)

        return d.to_string()

    print example_template(range(10))
    print
    print ItemTemplate(range(10)).render()
    print


    print bootstrap_example()