# ================
# Models
# represents data that will be stored and retrieved
# normally would go in a database (see SQLAlchemy), here it's just some plain classes and dictionaries
# ================


class Word(object):
    """Represents a word in the Cabbage language and it's translation to English."""
    def __init__(self, value, translation):
        self.value = value
        self.translation = translation
        self.tags = []
        lexicon[value] = self


# word index
lexicon = {}
# create some words
Word('cabbage', 'hello')
Word('cbg', 'hi / back')
Word('rhubarb', 'goodbye')
Word('rbrb', 'brb / afk')
Word('potato', 'how are you?')
Word('sprouts', 'sorry')
Word('banana', 'good')
Word('bananas', 'awesome')
Word('bean', 'bad')
Word('beans', 'horrible')
Word('yam', 'fuck')
Word('tomato', 'bitch')
Word('melon', 'thank you')
Word('watermelon', "you're welcome")
Word('peaches', 'ladies')
Word('pears', 'gentlemen')
Word('mushrooms', "I don't know")
Word('mushroom', 'dunno')
Word('avocado', 'I agree / I like it / yes')
Word('carrot', "I disagree / I don't like it / no")
Word('asparagus', 'assistance / help')
Word('peas', "brain fart / writer's block / confusion / confused / makes no sense")
Word('lettuce', "what? / what do you mean?")
Word('artichoke', 'are you joking? / are you kidding? / are you serious? dafuq?')


class Tag(object):
    """Groups words together."""
    def __init__(self, value, words):
        self.value = value
        self.words = []

        for w in words:
            word = lexicon[w]
            self.words.append(word)
            word.tags.append(self)

        tags[value] = self


# tag index
tags = {}
# create some tags
Tag('adjective', ['banana', 'bananas', 'bean', 'beans'])
Tag('expletive', ['yam', 'tomato'])
Tag('greeting', ['cabbage', 'cbg', 'potato'])


# ================
# Views
# accept some number of input input arguments (all the examples accept one)
# always return a list of (key, value) pairs to display
# ================

def search_lexicon(query):
    """Look up words starting with the query value."""
    found = [value for key, value in lexicon.items() if key.startswith(query)]

    if not found:
        return [('Nothing found', None)]

    return [('Results', ', '.join(x.value for x in found))]


def search_tags(query):
    """Look up tags starting with the query value."""
    found = [value for key, value in tags.items() if key.startswith(query)]

    if not found:
        return [('Nothing found', None)]

    return [('Results', ', '.join(x.value for x in found))]


def get_word(value):
    """Show details about a single word."""
    word = lexicon.get(value)

    if word is None:
        return [('Not found', None)]

    return [
        ('Word', word.value),
        ('Translation', word.translation),
        ('Tags', ', '.join(x.value for x in word.tags))
    ]


def get_tag(value):
    """Show details about a single tag."""
    tag = tags.get(value)

    if tag is None:
        return [('Not found', None)]

    return [
        ('Tag', tag.value),
        ('Words', ', '.join(x.value for x in tag.words))
    ]


# ================
# Controller
# handles user input, calling views, and printing results
# ================

# map segments into chains that lead to a view function
command_map = {
    'word': {
        'search': search_lexicon,
        'get': get_word
    },
    'tag': {
        'search': search_tags,
        'get': get_tag,
    },
}


def find_view(parts, search_space=None):
    """Consume items in a list to find a view in the command map.

    If a view is found return (view, unconsumed items)
    If no view is found, return (None, None)
    """
    if callable(search_space):
        return search_space, parts

    if search_space is None:
        search_space = command_map

    if not parts:
        return None, None

    x, remain = parts[0], parts[1:]

    if x in search_space:
        return find_view(remain, search_space[x])

    return None, None


def output(data):
    """Print result of view to terminal.

    Data is a list of 2-tuples.  Print them in order.
    If the second item in a tuple is None, just print the first item.
    Otherwise print in the format "first: second"
    """
    if not data:
        return

    for left, right in data:
        if right is None:
            print left
        else:
            print '{}: {}'.format(left, right)


def dispatch(input):
    """Try to call a view and output results based on user input.

    Input is a string of space separated commands.
    Consume input to find a view, then call the view with the remaining input.
    Output the results of the view, if a view was found.
    """
    parts = input.split(' ')
    view, args = find_view(parts)

    if view is None:
        output([('Command not found', None)])
        return

    data = view(*args)
    output(data)


def main():
    """Prompt for user input until EOF.

    For each input, call dispatch to handle the input.
    At EOF, output a parting message and quit.
    """
    while True:
        print
        try:
            input = raw_input('Enter command: ')
            print
        except EOFError:
            print
            print
            output([('Rhubarb', None)])
            print
            break
        else:
            dispatch(input)


if __name__ == '__main__':
    main()
