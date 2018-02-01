from itertools import chain
import inspect


# very naive deastruct implementation (not native...)

def _destruct(selector):
    def _(value):
        if isinstance(selector, dict):
            yield from chain.from_iterable(_destruct(selector[k])(value[k]) for k in selector)
            return
        if isinstance(selector, list):
            yield from chain.from_iterable(_destruct(a)(b) for a, b in zip(selector, value))
            return
        yield selector, value
    return _


def destruct(selector):
    def _(value):
        new_locals = dict(_destruct(selector)(value))
        # print('updating locals: %s' % new_locals)
        inspect.currentframe().f_back.f_locals.update(new_locals)
    return _