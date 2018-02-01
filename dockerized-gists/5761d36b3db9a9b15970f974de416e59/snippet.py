# sedlike.py - search/replace func from string roughly like 'sed -r s/old/new/g'

import functools

def search_replace(cmd, _cache={}):
    """Return a callable from sed/Perl-style search-replace pattern string.

    >>> search_replace('s/ham/spam/g')('ham-eggs-ham')
    'spam-eggs-spam'
    """
    try:
        return _cache[cmd]
    except KeyError:
        pass

    if not (cmd.startswith('s') and len(cmd) >= 6 and cmd.endswith('g')):
        raise ValueError('%r' % cmd)
    sep = cmd[1]
    if cmd.count(sep) != 3:
        raise ValueError('%r' % cmd)
    search, _, rest = cmd[2:].partition(sep)
    repl, _, rest = rest.partition(sep)
    if not search or rest != 'g':
        raise ValueError('%r' % cmd)

    use_mrab = any(v in search for v in ('(?V0)', '(?V1)'))
    if use_mrab:
        import regex as re
    else:
        import re

    regex = re.compile(search)
    result = _cache[cmd] = functools.partial(regex.sub, repl)
    result.cmd = cmd
    return result
