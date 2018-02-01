import re
import string as s


def tagify(*args, **kwargs):
    r'''Turns the argument strings into tags. so 'my tag' becomes '#MyTag'
    Any keyword arguments become tags with values.

    >>> tagify('hi there')
    ['#HiThere']
    >>> tagify('ho there', 'my_string', 'another-string')
    ['#HoThere', '#MyString', '#AnotherString']
    >>> tagify(my_kwarg = 33)
    ['#MyKwarg:33']
    >>> tagify(string_kwarg = 'hi there')
    ["#StringKwarg:'hi there'"]
    >>> tagify({'this is': 1, 'a dict arg' : 2})
    ['#ThisIs:1', '#ADictArg:2']
    >>> tagify('#AlreadyTagified')
    ['#AlreadyTagified']
    >>> tagify('#almost keyworded')
    ['#AlmostKeyworded']
    >>> tagify("""a_# d!ir*&ty-'t{"a.g@#""")
    ['#ADirtyTag']
    >>> tagify(['takes lists', '#too'], 'or whatever', ok = 'ok?')
    ['#TakesLists', '#Too', '#OrWhatever', "#Ok:'ok?'"]
    >>> tagify([['nested lists'],'should'],'work',['too'])
    ['#NestedLists', '#Should', '#Work', '#Too']
    >>> tagify([[[''],['',[],[]]],[[],[['']]]])
    []
    >>> tagify('','  ','-_-', "<(' '<) <(' ')> (>' ')>")
    []
    '''
    def _tagify_helper(arg):
        'Does tagification'
        # break existing camelcasing into spaces
        decameller = re.compile(r"([a-z])([A-Z])")
        decamelled = decameller.sub("\g<1> \g<2>", arg)
        # turn dashes and underscores to spaces
        spaced = decamelled.translate(s.maketrans('-_', '  '))
        # strip punctuation
        stripped = spaced.translate(s.maketrans('', ''), s.punctuation)
        # capitalize, delete spaces and add hash
        return '#' + s.capwords(stripped).replace(' ', '')

    tags = []
    for arg in args:
        if type(arg) is list:
            tags.extend(tagify(*arg))
        elif type(arg) is dict:
            tags.extend(tagify(**arg))
        else:
            tags.append(_tagify_helper(arg))
    for key, val in kwargs.iteritems():
        tags.append('{0}:{1}'.format(_tagify_helper(key), repr(val)))

    return [tag for tag in tags if tag != '#'] # filter empty tags