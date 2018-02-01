class Builder(object):
    _fields = None
    _to_build = None

    def __init__(self, to_build):
        self._fields = []
        self._to_build = to_build

    def _add_field(self, name):
        def inner(value):
            self._fields.append((name, value))
            return self
        return inner

    def __getattr__(self, name):
        return self._add_field(name)

    def build(self,):
        built = self._to_build()
        for field, value in self._fields:
            setattr(built, field, value)
        return built