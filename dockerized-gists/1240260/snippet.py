#coding: utf8

"""pymongoのAutoReferenceにパッチ当てるやつ

リスト内のDBRef全部にクエリを発行せずに{$in: [1,2,...,n]}する。

Example:
>>> from pymongo.son_manipulator import AutoReference, NamespaceInjector
>>> import autoreference_dbref_patch
"""

from bson.dbref import DBRef
from bson.son import SON
from pymongo.son_manipulator import AutoReference


def transform_outgoing(self, son, collection):
    """Replace DBRefs with embedded documents.
    """

    def transform_value(value):
        if isinstance(value, DBRef):
            return self._AutoReference__database.dereference(value)
        elif isinstance(value, list):
            #listの先頭がDBRefだったら1クエリで取ってくるようにする
            if value and isinstance(value[0], DBRef):
                return [o for o in self._AutoReference__database[value[0].collection].find({"_id": {"$in": [v.id for v in value]}})]
            else:
                return [transform_value(v) for v in value]
        elif isinstance(value, dict):
            return transform_dict(SON(value))
        return value

    def transform_dict(object):
        for (key, value) in object.items():
            object[key] = transform_value(value)
        return object

    return transform_dict(SON(son))
    

#AutoReferenceにmonkey patch
setattr(AutoReference, 'transform_outgoing', transform_outgoing)