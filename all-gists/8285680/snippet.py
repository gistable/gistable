ENGLISH_PREPOSITIONS = (
    'aboard',
    'about',
    'above',
    'across',
    'after',
    'against',
    'along',
    'amid',
    'among',
    'anti',
    'around',
    'before',
    'behind',
    'below',
    'beneath',
    'beside',
    'besides',
    'between',
    'beyond',
    'concerning',
    'considering',
    'despite',
    'down',
    'during',
    'except',
    'excepting',
    'excluding',
    'following',
    'from',
    'inside',
    'into',
    'like',
    'minus',
    'near',
    'onto',
    'opposite',
    'outside',
    'over',
    'past',
    'plus',
    'regarding',
    'round',
    'save',
    'since',
    'than',
    'that',
    'this',
    'through',
    'toward',
    'towards',
    'under',
    'underneath',
    'unlike',
    'until',
    'upon',
    'versus',
    'with',
    'within',
    'without',
)

PREPOSITION_RE = re.compile(r'(\s|^)(({})\s)+'.format('|'.join(ENGLISH_PREPOSITIONS)))
SMALLWORDS_RE = re.compile(r'(\s|^)(([a-zA-Z-_(]{1,2}(\'|’)*[a-zA-Z-_,;]{0,1}?\s)+)')
DASHES_RE = re.compile(r'([-–—])\s')
EMPHASIS_RE = re.compile(r'(<(strong|em|b|i)>)(([^\s]+\s*){2,3})?(<\/(strong|em|b|i)>)')


def preposition_match(match_obj):
    groups = match_obj.groups()
    return groups[0] + re.sub('\s', '&nbsp;', groups[1])


def preposition_replacer(text):
    return PREPOSITION_RE.sub(preposition_match, text)


def smallwords_match(match_obj):
    groups = match_obj.groups()
    return groups[0] + re.sub('\s', '&nbsp;', groups[1])


def smallwords_replacer(text):
    return SMALLWORDS_RE.sub(smallwords_match, text)


def dashes_match(match_obj):
    groups = match_obj.groups()
    return re.sub('\s', '&nbsp;', groups[0])


def dashes_replacer(text):
    return DASHES_RE.sub(dashes_match, text)


def emphasis_match(match_obj):
    groups = match_obj.groups()
    return groups[0] + re.sub('\s', '&nbsp;', groups[2]) + groups[4]


def emphasis_replacer(text):
    return EMPHASIS_RE.sub(emphasis_match, text)


def func_chain(funcs, data):
    return reduce((lambda x, y: y(x)), funcs, data)


def ragadjust(text):
    return func_chain((
        preposition_replacer,
        smallwords_replacer,
        dashes_replacer,
        emphasis_replacer
    ), text)