from sqlalchemy.ext.declarative import declarative_base

class Mixin:
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    def as_clear_dict(self):
        _dict = {}
        for c in self.__table__.columns:
            if c.foreign_keys:
                continue
            val = getattr(self, c.name)
            if val:
                _dict[c.name] = val
        return _dict

Base = declarative_base(cls=Mixin)