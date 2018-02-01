import lxml.etree
def pprint(elem):
    print lxml.etree.tostring(elem, pretty_print=True)

class Bind(object):
    def __init__(self, path, converter=None, first=False):
        '''
        path -- xpath to select elements
        converter -- run result through converter
        first -- return only first element instead of a list of elements
        '''
        self.path = path
        if converter is None:
            converter = lambda x: x
        self.converter = converter
        self.first = first

    def __get__(self, instance, owner=None):
        res = instance._elem.xpath(self.path)
        if self.first:
            return self.converter(res[0])
        return [self.converter(r) for r in res]


class Text(Bind):
    '''uses converter to select text from node and set default to first element only
    '''
    def __init__(self, path, first=True):
        converter = lambda x: x.text
        Bind.__init__(self, path, converter, first=first)

class Integer(Bind):
    '''uses converter to select text from node and set default to first element only
    '''
    def __init__(self, path, first=True):
        Bind.__init__(self, path, self.convert, first=first)

    def convert(self, x):
        if isinstance(x, lxml.etree._Element):
            x = x.text
        return int(x)

import dateutil.parser

test_response = '''
<ISBNdb server_time="2010-07-21T15:56:06Z">
    <BookList total_results="1">
        <BookData book_id="programming_collective_intelligence" isbn="0596529325">
            <Title>Programming collective intelligence</Title>
            <AuthorsText>Toby Segaran</AuthorsText>
            <PublisherText publisher_id="oreilly">O'Reilly, 2007.</PublisherText>
        </BookData>
    </BookList>
</ISBNdb>
'''


class Data(object):
    def __init__(self, elem):
        self._elem = elem

class Book(Data):
    title = Bind('Title/text()', first=True) #use xpath text() to get text 
    author = Text('AuthorsText')             #get the text via a converter
    publisher = Text('PublisherText')
    publisher_id = Bind('PublisherText/@publisher_id', first=True)

class ISBNdb(Data):

    server_time = Bind('@server_time', dateutil.parser.parse, first=True)
    total_results = Integer('BookList/@total_results')
    books = Bind('//BookData', Book)
