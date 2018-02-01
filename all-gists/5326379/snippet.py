"""
    This small module makes it easy to bake PNG images with links to
    Open Badge assertions. It also allows for easy retrieval of the link
    from baked PNGs.

    For more information on badge baking, see:

        https://github.com/mozilla/openbadges/wiki/Badge-Baking

    Note that this module requires the PyPNG module:

        http://pythonhosted.org/pypng/

    The module can be installed via 'pip install pypng'.
"""

import os
import png

def get_baked_url(src):
    """
    Return the assertion URL contained in the given baked PNG. If
    the image isn't baked, return None.

    Example:

        >>> get_baked_url('baked.png')
        'http://f.org/assertion.json'
    """

    if isinstance(src, basestring): src = open(src, 'rb')
    reader = png.Reader(file=src)
    for chunktype, content in reader.chunks():
        if chunktype == 'tEXt' and content.startswith('openbadges\x00'):
            return content.split('\x00')[1]

def bake_badge(src, dest, url):
    """
    Bake the given PNG file with the given assertion URL. The source and
    destination can be filenames or file objects.

    Example:

        >>> bake_badge('unbaked.png', 'baked.png', 'http://f.org/a.json')
    """

    if isinstance(src, basestring): src = open(src, 'rb')
    if isinstance(dest, basestring): dest = open(dest, 'wb')

    reader = png.Reader(file=src)
    chunks = [
        (chunktype, content)
        for chunktype, content in reader.chunks()
        if not (chunktype == 'tEXt' and content.startswith('openbadges\x00'))
    ]

    chunks.insert(1, ('tEXt', '\x00'.join(('openbadges', url))))
    png.write_chunks(dest, chunks)

def test(show_output=False):
    """
    Test suite for this module.
    """

    from StringIO import StringIO

    def eq(a, b, msg):
        if show_output: print "%-60s" % msg,
        if a != b:
            raise AssertionError('%s (%s != %s)' % (msg, repr(a), repr(b)))
        if show_output: print "OK"

    PNG = '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00' \
          '\x10\x08\x02\x00\x00\x00\x90\x91h6\x00\x00\x00\x19IDAT(\x91c' \
          '\xfc\xff\xff?\x03)\x80\x89$\xd5\xa3\x1aF5\x0c)\r\x00Um\x03' \
          '\x1d\xe4FZ\x12\x00\x00\x00\x00IEND\xaeB`\x82'

    unbaked = StringIO(PNG)
    eq(get_baked_url(unbaked), None,
       'get_baked_url() on unbaked badge returns None')

    unbaked = StringIO(PNG)
    baked = StringIO()
    bake_badge(unbaked, baked, 'http://foo.org/assertion.json')

    baked = StringIO(baked.getvalue())
    eq(get_baked_url(baked), 'http://foo.org/assertion.json',
       'baking an unbaked badge works')

    baked = StringIO(baked.getvalue())
    rebaked = StringIO()
    bake_badge(baked, rebaked, 'http://another/assertion')

    rebaked = StringIO(rebaked.getvalue())
    eq(get_baked_url(rebaked), 'http://another/assertion',
       'baking an already-baked badge re-bakes it')

if __name__ == '__main__':
    test(show_output=True)
