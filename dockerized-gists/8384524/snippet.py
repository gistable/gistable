import re
import itertools
import collections
import textwrap
import random
import shelve
import contextlib

workman_lessons = [
        ('tn',       '',                    'home row-first finger',     'ngrams'),
        ('he',       '',                    'home row-second finger',    'ngrams'),
        ('he',       'tn',                  'home row-two fingers',      'words'),
        # ('then',   '',                    'home row-two fingers',      'ngrams'),
        ('so',       '',                    'home row-third finger',     'ngrams'),
        ('so',       'then',                'home row-three fingers',    'words'),
        ('ai',       '',                    'home row-fourth finger',    'ngrams'),
        ('asht',     '',                    'home row-left hand',        'words'),
        ('noei',     '',                    'home row-right hand',       'words'),
        ('ashtneoi', '',                    'home row-both hands',       'ngrams'),
        ('ashtneoi', '',                    'home row-both hands',       'words'),
        ('lr',       '',                    'lr',                        'ngrams'),
        ('lr',       'ashtneoi',            'homerow + lr',              'ngrams'),
        ('lr',       'ashtneoi',            'homerow + lr',              'words'),
        ('cudp',     '',                    'cudp',                      'ngrams'),
        ('cudp',     'ashtneoi',            'cudp + homerow',            'ngrams'),
        ('cudp',     'ashtneoi',            'cudp + homerow',            'words'),
        ('gy',       '',                    'gy',                        'ngrams'),
        ('gy',       'ashtneoi',            'gy + homerow',              'ngrams'),
        ('gy',       'ashtneoi',            'gy + homerow',              'words'),
        ('mfw',      '',                    'mfw',                       'ngrams'),
        ('mfw',      'ashtneoi',            'mfw + homerow',             'ngrams'),
        ('mfw',      'ashtneoi',            'mfw + homerow',             'words'),
        ('kb',       '',                    'kb',                        'ngrams'),
        ('kb',       'ashtneoi',            'kb + homerow',              'ngrams'),
        ('kb',       'ashtneoi',            'kb + homerow',              'words'),
        ('cudp',     'lrashtneoi',          'cumulative including cudp', 'words'),
        ('gy',       'cudplrashtneoi',      'cumulative including gy',   'words'),
        ('mfw',      'cudplrgyashtneoi',    'cumulative including mfw',  'words'),
        ('kb',       'mfwcudplrgyashtneoi', 'cumulative including kb',   'words'),
]


"""
given some letters to drill on:
    - drill on ngrams
    - drill on words
        - 3x each then random order 3x
        - if there's too many words, do a random sample.
"""

def ngrams(letters, extraletters, dictionary):
    """from the given set of letters, discover the frequency for which each
    possible permutation appears within dictionary words. create a drill
    according to this frequency.

    if naive=True, don't calculate frequency, just determine if the
    combination appears at all in any dictionary words. this is faster.

    """
    possible_re = re.compile(r'[%s]{3,}' % (letters+extraletters))
    valid_re = re.compile(r'[%s]' % letters)
    memo = collections.Counter()
    for word in dictionary:
        for match in possible_re.findall(word):
            memo[match] += 1
    for ngram in memo:
        if valid_re.search(ngram):
            yield (memo[ngram], ngram)


def find_words(letters, extraletters, dictionary, min_length=2):
    """from the given set of letters, discover which words may be
    created from them.

    """
    word_re = re.compile(r'^[%s]{%s,}$' % (letters+extraletters, min_length))
    valid_re = re.compile(r'.*[%s]' % letters)

    return (word for word in dictionary if word_re.match(word) and valid_re.match(word))


def wordlesson(words):
    """generate a lesson from the given words:

    - for each word, repeat 3x
    - all words, random order, repeat 3x
    """
    words = list(words)
    for word in words:
        yield " ".join([word] * 3)
    for x in range(3):
        random.shuffle(words)
        yield " ".join(words)


def gtypist_lesson(label, words, title=None, instructions=None):
    """Given a title, instructions, and word list, generate lines in
    gtypist format.
    """
    tw = textwrap.TextWrapper(subsequent_indent=" :")
    yield "*:%s" % label
    if title:
        tw.initial_indent="B:"
        yield tw.fill(title)
    if instructions:
        tw.initial_indent="T:"
        yield tw.fill(instructions)
    tw.initial_indent="D:"
    yield tw.fill(" ".join(words))


def menu(labels):
    yield "*:MENU"
    yield "B:Workman Lessons"
    yield 'M: UP=_EXIT "These are lessons for learning the workman keyboard layout."'
    for label, title in labels:
        yield ' :%s "%s"' % (label, title)


def full_lesson(dictionary):
    wordsused = set()
    labels = []
    for n, (letters, extraletters, description, lessontype) in enumerate(workman_lessons):
        if lessontype == 'ngrams':
            words = ngrams(letters, extraletters, dictionary)
            # omit 0-frequency ngrams
            words = set(ng for ng in words if ng[0])
            # take 20 most-frequent ngrams
            lesson_words = set(w for f, w in sorted(words, reverse=True)[:10])
            for x in letters:
                lesson_words.add(x)
            lesson_words = wordlesson(lesson_words)
            instructions = " ".join(x.strip() for x in """
                a drill on word pieces including the letters
                %s. (%d found)""".strip().splitlines()) % (", ".join(letters), len(words))
            title = "%s %s drill" % (description, lessontype)
            label = "lesson_%d" % n
            labels.append((label, title))
            yield gtypist_lesson(
                    label,
                    lesson_words,
                    title=title,
                    instructions=instructions)
        elif lessontype == 'words':
            words = set(find_words(letters, extraletters, dictionary))
            # don't use words from previous lessons
            words -= wordsused
            wordsused |= words
            # if we have a lot of words, make a few lessons.
            for lesson_number in range(min((len(words)-1)/10+1, 3)):
                if len(words) >= 10:
                    lesson_words = set(random.sample(words, 10))
                else:
                    lesson_words = set(words)
                words -= lesson_words
                lesson_words = wordlesson(lesson_words)
                instructions = " ".join(x.strip() for x in """
                    a drill on words that include the letters %s. (Set
                    %d) (%d remaining in dictionary)""".strip().splitlines()) % (
                            ", ".join(letters), lesson_number,
                            len(words))
                title = "%s %s drill #%d" % (description, lessontype, lesson_number + 1)
                label = "lesson_%d_%d" % (n, lesson_number)
                labels.append((label, title))
                yield gtypist_lesson(
                        label,
                        lesson_words,
                        title=title,
                        instructions=instructions)
        else:
            raise ValueError("unknown lesson type", lessontype)

    yield menu(labels)

def main(argv0):

    dictionary_filename = '/usr/share/dict/american-english-huge'
    dictionary_filename = '/usr/share/dict/words'

    dictionary = set(word.strip() for word in open(dictionary_filename))

    print "G:MENU"
    for lesson in full_lesson(dictionary):
        print "\n".join(lesson)
        print

if __name__=="__main__":
    import sys
    raise SystemExit(main(*sys.argv))
