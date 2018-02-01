class DictLike(object):
    def __contains__(self, key):
        try:
            ignored = self[key]
            return True
        except KeyError:
            return False
    has_key = __contains__

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

class CollectionContainer(DictLike):
    collections = {}

    def __getitem__(self, key):
        cls = self.collections[key]
        obj = cls(self.__parent__.session, self, key)
        obj.__parent__ = self
        obj.__name__ = key
        return obj

class Collection(DictLike):
    key = "id"
    order_by = "id"

    def __init__(self, session, parent_instance=None, relation_attr=None):
        self.session = session
        self.parent_instance = parent_instance
        self.relation_attr = relation_attr

    def query(self):
        query = self.session.query(self.model)
        if self.parent_instance:
            query = query.with_parent(self.parent_instance, self.relation_attr)
        query = query.order_by(getattr(self.model, self.order_by))
        return query

    def __iter__(self):
        for obj in self.query():
            obj.__parent__ = self
            obj.__name__ = str(getattr(obj, self.key))
            yield obj

    def __getitem__(self, key):
        query = self.query()
        query = query.filter(getattr(self.model, self.key) == key)
        result = query.first()
        if result is None:
            raise KeyError(key)
        result.__name__ = key
        result.__parent__ = self
        return result

    def add(self, obj):
        assert isinstance(obj, self.model)
        if self.parent_instance:
            relation = getattr(self.parent_instance, self.relation_attr)
            relation.append(obj)
        else:
            self.session.add(obj)
        self.session.flush()
        obj.__name__ = str(getattr(obj, self.key))
        obj.__parent__ = self

    def remove(self, obj):
        key = str(getattr(obj, self.key))
        assert self[key] == obj
        del obj.__name__
        del obj.__parent__
        self.session.delete(obj)
        self.session.flush()

    def __delitem__(self, key):
        self.remove(self[key])

def RootFactory(session_factory, **collections):
    class Root(dict):
        def __init__(self, request):
            super(Root, self).__init__()
            self.__parent__ = None
            self.__name__ = None
            self.session = session_factory()
            for name, cls in collections.items():
                obj = cls(self.session)
                obj.__name__ = name
                obj.__parent__ = self
                self[name] = obj
                setattr(self, name, obj)
    return Root
