from itertools import chain, starmap

def remove_spans(s, spans):
    to_drop = set(chain(*starmap(range, spans)))
    return ''.join(c for (i, c) in enumerate(s) if i not in to_drop)
