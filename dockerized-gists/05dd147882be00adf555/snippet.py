"""
Use ERPPeek or OOOP interface compatible insed OpenERP.

Ex.
client = PoolWrapper(pool, cursor, uid)
client.ResPartner.search([])
partner_obj = client.ResPartner

partner_obj.write([1], {'name': 'Fooo!'})
"""
from functools import partial
import re

__FIRST_CAP_RE = re.compile('(.)([A-Z][a-z]+)')
__ALL_CAP_RE = re.compile('([a-z0-9])([A-Z])')


def lowercase(name):
    s1 = __FIRST_CAP_RE.sub(r'\1.\2', name)
    return __ALL_CAP_RE.sub(r'\1.\2', s1).lower()
    

class PoolWrapper(object):
    def __init__(self, pool, cursor, uid):
        self.pool = pool
        self.cursor = cursor
        self.uid = uid

    def __getattr__(self, name):
        model = lowercase(name)
        return ModelWrapper(self.pool.get(model), self.cursor, self.uid)


class ModelWrapper(object):
    def __init__(self, model, cursor, uid):
        self.model = model
        self.cursor = cursor
        self.uid = uid

    def wrapper(self, method):
        return partial(method, self.cursor, self.uid)

    def __getattr__(self, item):
        base = getattr(self.model, item)
        if callable(base):
            return lambda *args: self.wrapper(base)(*args)
        else:
            return base