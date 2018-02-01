from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()

def db_model_repr(self):
    """Create a automatic meaningful repr for db.Model classes

    Usage example:
    class MyClass(db.Model):
        __repr__ = db_model_repr
    """
    fields = [str(x).split('.')[-1] for x in self.__table__.c]
    values = ["{}={!r}".format(field, getattr(self, field)) for field in fields]
    return "{}({})".format(self.__class__.__name__, ', '.join(values))
