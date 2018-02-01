from html.entities import name2codepoint
from html.parser import HTMLParser


class SlackifyHTML(HTMLParser):

    def __init__(self, html, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.output = ''

        self.feed(html)

    def handle_starttag(self, tag, attrs):

        if tag == 'b' or tag == 'strong':
            self.output += '*'
        if tag == 'i' or tag == 'em':
            self.output += '_'
        if tag == 'code':
            self.output += '`'
        if tag == 'a':
            self.output += '<'
            for attr in attrs:
                self.output += attr[1] + '|'

    def handle_endtag(self, tag):

        if tag == 'b' or tag == 'strong':
            self.output += '*'
        if tag == 'i' or tag == 'em':
            self.output += '_'
        if tag == 'a':
            self.output += '>'
        if tag == 'code':
            self.output += '`'

    def handle_data(self, data):
        self.output += data

    def handle_comment(self, data):
        pass

    def handle_entityref(self, name):
        c = chr(name2codepoint[name])
        pass

    def handle_charref(self, name):
        if name.startswith('x'):
            c = chr(int(name[1:], 16))
        else:
            c = chr(int(name))

    def handle_decl(self, data):
        pass

    def get_output(self):

        return ' '.join(self.output.split())