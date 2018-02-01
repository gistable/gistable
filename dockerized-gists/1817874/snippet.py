# -*- coding: utf-8 -*-
#
# Used like this:
#
# from repermute import ipermute
#
# for s in ipermute('[A-Z]\d'):
#    print s
#
# Almost all regular expression constructs are supported except for '*'
# (which in the Python sre_parse implementation matches 0 to 65535
# times), '+' and '^'. Non-ASCII characters doesn't work, but I think
# that is a limitation in the sre_parse module. It works by first
# parsing the regexp to string sequences so that [A-Z] becomes ['A',
# 'B', ... 'Z'], \d becomes ['1', ... , '9']. Then a Cartesian join is
# applied on all string sequences to get all possible permutations of
# them all.

import itertools
from sre_constants import *
import sre_parse
import string

category_chars = {
    CATEGORY_DIGIT : string.digits,
    CATEGORY_SPACE : string.whitespace,
    CATEGORY_WORD  : string.digits + string.letters + '_'
    }

def unique_extend(res_list, list):
    for item in list:
        if item not in res_list:
            res_list.append(item)

def handle_any(val):
    """
    This is different from normal regexp matching. It only matches
    printable ASCII characters.
    """
    return string.printable

def handle_branch((tok, val)):
    all_opts = []
    for toks in val:
        opts = permute_toks(toks)
        unique_extend(all_opts, opts)
    return all_opts

def handle_category(val):
    return list(category_chars[val])

def handle_in(val):
    out = []
    for tok, val in val:
        out += handle_tok(tok, val)
    return out

def handle_literal(val):
    return [chr(val)]

def handle_max_repeat((min, max, val)):
    """
    Handle a repeat token such as {x,y} or ?.
    """
    subtok, subval = val[0]

    if max > 5000:
        # max is the number of cartesian join operations needed to be
        # carried out. More than 5000 consumes way to much memory.
        raise ValueError("To many repetitions requested (%d)" % max)

    optlist = handle_tok(subtok, subval)

    iterlist = []
    for x in range(min, max + 1):
        joined = join([optlist] * x)
        iterlist.append(joined)

    return (''.join(it) for it in itertools.chain(*iterlist))

def handle_range(val):
    lo, hi = val
    return (chr(x) for x in range(lo, hi + 1))

def handle_subpattern(val):
    return list(permute_toks(val[1]))

def handle_tok(tok, val):
    """
    Returns a list of strings of possible permutations for this regexp
    token.
    """
    handlers = {
        ANY        : handle_any,
        BRANCH     : handle_branch,
        CATEGORY   : handle_category,
        LITERAL    : handle_literal,
        IN         : handle_in,
        MAX_REPEAT : handle_max_repeat,
        RANGE      : handle_range,
        SUBPATTERN : handle_subpattern}
    try:
        return handlers[tok](val)
    except KeyError, e:
        fmt = "Unsupported regular expression construct: %s"
        raise ValueError(fmt % tok)

def permute_toks(toks):
    """
    Returns a generator of strings of possible permutations for this
    regexp token list.
    """
    lists = [handle_tok(tok, val) for tok, val in toks]
    return (''.join(it) for it in join(lists))

def join(iterlist):
    """
    Cartesian join as an iterator of the supplied sequences. Borrowed
    from:
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/302478
    """
    def rloop(seqin, comb):
        if seqin:
            for item in seqin[0]:
                newcomb = comb + [item]
                for item in rloop(seqin[1:], newcomb):
                    yield item
        else:
            yield comb
    return rloop(iterlist, [])

########## PUBLIC API ####################

def ipermute(p):
    toks = [tok_n_val for tok_n_val in sre_parse.parse(p)]
    return permute_toks(toks)

def permute(p):
    return list(ipermute(p))