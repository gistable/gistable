class Factory(object):
    model = object

    def __init__(self):
        self._objs = {}

    def create(self, name):
        self._objs[name] = type(name, self.model.__bases__, dict(self.model.__dict__))
        return self._objs[name]

    def get(self, name):
        return self._objs.get(name)

    def new(self, name):
        return self._objs[name]()
