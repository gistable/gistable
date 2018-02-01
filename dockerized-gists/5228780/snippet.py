# -*- coding: utf-8 -*-

IRREGULAR_PLURALS = {'alumnus': 'alumni',
                    'cactus': 'cacti',
                    'focus': 'foci',
                    'fungus': 'fungi',
                    'nucleus': 'nuclei',
                    'radius': 'radii',
                    'stimulus': 'stimuli',
                    'axis': 'axes',
                    'analysis': 'analyses',
                    'basis': 'bases',
                    'crisis': 'crises',
                    'diagnosis': 'diagnoses',
                    'ellipsis': 'ellipses',
                    'hypothesis': 'hypotheses',
                    'oasis': 'oases',
                    'paralysis': 'paralyses',
                    'parenthesis': 'parentheses',
                    'synthesis': 'syntheses',
                    'synopsis': 'synopses',
                    'thesis': 'theses',
                    'appendix': 'appendices',
                    'index': 'indeces',
                    'matrix': 'matrices',
                    'beau': 'beaux',
                    'bureau': 'bureaus',
                    'tableau': 'tableaux',
                    'child': 'children',
                    'man': 'men',
                    'ox': 'oxen',
                    'woman': 'women',
                    'bacterium': 'bacteria',
                    'corpus': 'corpora',
                    'criterion': 'criteria',
                    'curriculum': 'curricula',
                    'datum': 'data',
                    'genus': 'genera',
                    'medium': 'media',
                    'memorandum': 'memoranda',
                    'phenomenon': 'phenomena',
                    'stratum': 'strata',
                    'deer': 'deer',
                    'fish': 'fish',
                    'means': 'means',
                    'offspring': 'offspring',
                    'series': 'series',
                    'sheep': 'sheep',
                    'species': 'species',
                    'foot': 'feet',
                    'goose': 'geese',
                    'tooth': 'teeth',
                    'antenna': 'antennae',
                    'formula': 'formulae',
                    'nebula': 'nebulae',
                    'vertebra': 'vertebrae',
                    'vita': 'vitae',
                    'louse': 'lice',
                    'mouse': 'mice'}


def noun_number(word, num):
    if num == 1:
        return singularize(word)
    if num >= 2:
        return pluralize(word)


def singularize(word):
    for s, p in IRREGULAR_PLURALS.iteritems():
        if p == word:
            return s
    try:
        if len(word) == 2 and word[-1:] == 's':
            # or just return word?
            return word[:-1]
        if word[-3] == 'ies' and word[-4] not in 'aeiou':
            return word[:-3] + 'y'
        if word[-2:] == 'ii':
            return word[:-1] + 'us'
        if word[-2:] == 'es':
            return word[:-2]
        if word[-1:] == 's':
            return word[:-1]
        # not singular enough?
        return word
    except IndexError:
        return word


def pluralize(word):
    if word in IRREGULAR_PLURALS:
        return IRREGULAR_PLURALS[word]
    try:
        if word[-1] == 'y' and word[-2] not in 'aeiou':
            return word[:-1] + 'ies'
        if word[-1] == 's':
            return word + 'es'
        if word[-2:] in ('ch', 'sh'):
            return word + 'es'
        return word + 's'
    except IndexError:
        return word + 's'
