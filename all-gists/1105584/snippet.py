#!/usr/bin/env python
#coding: utf8
#################################### IMPORTS ###################################

# Std Libs
import re

from re import sre_parse, sre_compile
from itertools import izip, islice

#################################### README ####################################

""" Horrible, horrible implementation of sorting, by selector bestmatch """

################################################################################

def memoize(func):
    "Implementation taken from python test suite"
    saved = {}
    def call(*args):
        try:
            return saved[args]
        except KeyError:
            res = func(*args)
            saved[args] = res
            return res
        except TypeError:
            # Unhashable argument
            return func(*args)
    call.func_name = func.func_name
    return call

@memoize
def normalize_scope(scope):
    """ Sublime returns scopes that are not sane!

        >>> for pt in xrange(0, view.size()):
        >>>     scope = view.syntaxName(pt)
        >>>     assert view.matchSelector(pt, normalize_scope(scope))

    """

    return ' '.join(reversed(map(unicode.strip, scope.split())))

@memoize
def simple_specificity(selector, scope):
    if re.match(re.escape(selector) + '(\.|$)', scope):
        # scope.startswith(selector):
        return selector.count('.') + 1

@memoize
def single_selector_specificity(selector, scope):
    all_selectors, all_scopes = [s.split() for s in (selector, scope)]

    specificity = []
    level = len(all_scopes)

    for n, simple_selector in enumerate(reversed(all_selectors)):

        for i, simple_scope in enumerate(reversed(all_scopes[:level])):
            spec = simple_specificity(simple_selector, simple_scope)

            if spec:
                specificity.insert(0, (level-i, spec))
                level -= (i+1)
                break

        if n+1 != len(specificity):
            return []

    return specificity

################################# SCOPE PARSER #################################

class operator(unicode): pass

@apply
def scanner():

    def s_ident(scanner, token):      return token.strip()
    def s_operator(scanner, token):   return operator(token)
    def s_expression(scanner, token): return scanner.scan(token[1:-1])[0]

    return re.Scanner ([
        ( r"\(.*?\)",                           s_expression),
        ( r"(([a-z][a-z-]*[a-z]?\.?)+ ?)+",     s_ident),
        ( r"(,|\|\||-)",                        s_operator),
        ( r"\s+",                               None)
    ])

############################# SELECTOR SPECIFICITY #############################

def compare_candidates(c1, c2):
    for t1, t2 in izip(reversed(c1), reversed(c2)):
        either_is_greater     = cmp(t1, t2)
        if either_is_greater: return either_is_greater

    return cmp(len(c1), len(c2))

def sort_candidates(candidates, key=lambda i: i[0], reverse=True):
    return sorted(candidates, cmp=compare_candidates, key=key, reverse=reverse )

@memoize
def selector_specificity(selector, scope):
    if not isinstance(selector, list):
        selector, jibberish = scanner.scan(selector)
        if jibberish: print repr(jibberish)

    prev_operation = operation = None
    candidates = []

    for token in selector:
        if not isinstance(token, operator):
            if isinstance(token, list):
                specificity = selector_specificity(token, scope)

            elif not (operation == '-' and not candidates):
                specificity = single_selector_specificity(token, scope)

            if operation == '-':
                if candidates and specificity and prev_operation != '-':
                    candidates.pop()

            elif specificity:
                candidates.append(specificity)
        else:
            prev_operation = operation
            operation = token

    return sorted(candidates, cmp=compare_candidates)[-1] if candidates else []

def sort_by_scope (  scope,
                     to_sort,
                     scope_index=0,
                     keep_non_matches=True ):

    candidates =[]

    for i, item in enumerate(to_sort):
        selector = item[scope_index]
        specificity = selector_specificity( selector, scope )

        if specificity or keep_non_matches:
            candidates.append((specificity, i ))

    return [to_sort[i[1]] for i in sort_candidates(candidates)]

class selector_map(dict):
    def all(self, scope):
        return sort_by_scope(scope, self.items(), keep_non_matches=False)

    def __getitem__(self, item):
        candidates = self.all(item)
        if candidates: return candidates[0][1]

##################################### TESTS ####################################

if 1:
    assert selector_specificity('a,    a.b.c -d -z', 'a.b.c d') == [(1, 1)]
    assert selector_specificity('a -d, a.b.c -d -z', 'a.b.c d') == []

    assert selector_specificity('a || a.b.c -d -z',  'a.b.c d') == [(1, 1)]

    assert ( scanner.scan('punctuation string - meta.monkey-balls') ==
             (['punctuation string', '-', 'meta.monkey-balls'], '') )

    assert simple_specificity('selector', 'selector.rules') == 1
    assert simple_specificity('selector.rules.monkey', 'selector.rules') is None

    assert single_selector_specificity (
        'string punctuation',
        'text.xml meta.tag.xml string.quoted.double.xml '
        'punctuation.definition.string.begin.xml' ) == [(3, 1), (4, 1)]

    assert single_selector_specificity (
        'string',
        u'text.xml meta.tag.xml string.quoted.double.xml punctuation.definition.string.begin.xml'
    ) == [(3, 1)]

    assert simple_specificity('entity.name.function', 'entity.name.function.python') == 3
    assert selector_specificity('entity.name.function', 'source.python meta.function.python entity.name.function.python') == [(3, 3)]

    a_scope = 'text.html.basic meta.tag.block.any.html meta-attribute-with-value.id.html entity.other.attribute-name.id.html'
    c1 = selector_specificity('meta.tag entity', a_scope)
    c2 = selector_specificity('entity.other.attribute-name.id.html', a_scope)

    assert sorted([c1, c2], cmp=compare_candidates)[1] == c2

################################################################################