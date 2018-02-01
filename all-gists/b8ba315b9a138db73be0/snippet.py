from lxml import etree
import premailer


class MyPremailer(premailer.Premailer):
    def transform(self, pretty_print=True, **kwargs):
        assert self.method == 'html'

        parser = etree.HTMLParser()
        stripped = self.html.strip()

        self.html = etree.fromstring(stripped, parser)

        tree = super(MyPremailer, self).transform(pretty_print, **kwargs)

        self_closing = ['area', 'base', 'br', 'col', 'command', 'embed', 'hr',
                        'img', 'input', 'keygen', 'link', 'meta', 'param',
                        'source', 'track', 'wbr']

        def tostring(tree):
            print(type(tree))
            if isinstance(tree.tag, basestring):
                attr = ['{}="{}"'.format(k, v.replace('"', "'")) for k, v
                        in tree.items()]
                attr = ' '.join(attr)
                if tree.tag in self_closing:
                    assert len(tree) == 0
                    if attr:
                        s = '<{} {}/>'.format(tree.tag, attr)
                    else:
                        s = '<{}/>'.format(tree.tag)
                else:
                    if attr:
                        s = '<{} {}>'.format(tree.tag, attr)
                    else:
                        s = '<{}>'.format(tree.tag)
                    if tree.text:
                        s += tree.text
                    else:
                        s += ''
                    for element in tree.iterchildren():
                        s += tostring(element)
                    s += '</{}>'.format(tree.tag)
            elif isinstance(tree, etree._Comment):
                s = '<!--{}-->'.format(tree.text)
            else:
                assert False, 'Unknown element type: {}'.format(type(tree))
            if tree.tail:
                s += tree.tail
            return s

        return tostring(tree.getroot())
