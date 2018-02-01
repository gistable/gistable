import re
from functools import reduce


def test_handles_words_with_vowels():
    assert pig_latin('egg') == 'eggway'


def test_handles_words_starting_with_consonat():
    assert pig_latin('happy') == 'appyhay'


def test_handles_words_starting_with_multiple_consonats():
    assert pig_latin('glove') == 'oveglay'


def test_proper_capitalization():
    assert pig_latin('Duck') == 'Uckday'


def test_proper_uppercase_and_lowercase_formating():
    assert pig_latin('DUCK') == 'UCKDAY'


VOWEL_SEQ = 'aeiou'
CONS_ROOT_RE = re.compile(
    '^(?P<cons>[^{}]*)(?P<root>.*)$'.format(VOWEL_SEQ),
    re.IGNORECASE,
)


def always(word):
    return True


def pig_shufle(word):
    cons, root = consonant_split(word)
    return ''.join([root, cons, sufix(cons)])


def sufix(cons):
    return 'ay' if cons else 'way'


def consonant_split(word):
    return CONS_ROOT_RE.match(word).groups()


TRANSFORM_MATCH_SEQ = (
    (pig_shufle, always),
    (str.title, str.istitle),
    (str.upper, str.isupper),
)


def apply_transform(word, transform):
    return transform(word)


def pig_latin(word):
    transform_seq = (tr[0] for tr in TRANSFORM_MATCH_SEQ if tr[1](word))
    return reduce(apply_transform, transform_seq, word)