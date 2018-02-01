import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base, declared_attr


class HookEventHandler(object):
    """
    registers itself with the mapper for whatever event name passed in
    looks for corresponding event_name attribute on target and calls
    it if it exists
    """
    def __init__(self, mapper, event_name):
        sa.event.listen(mapper, event_name, self)
        self.event_name = event_name

    def __call__(self, mapper, connection, target):
        hook = getattr(target, self.event_name, None)
        if hook:
            return hook()

    @classmethod
    def register(cls):
        for action in ("insert", "update", "delete"):
            for occurs in ("before", "after"):
                event_name = "%s_%s" % (occurs, action)
                # side-effect
                cls(sa.orm.mapper, event_name)

HookEventHandler.register()


#Example
class MyBase(object):
    """
    base class for all models.
    __tablename__ defaults to class name
    """
    @declared_attr
    def __tablename__(cls):
        return cls.__name__

    def before_insert(self):
        pass  # run before data is written to the database
    def before_update(self):
        pass # run before data is written to the database
    def before_delete(self):
        pass  # run before data is written to the database
    def after_insert(self):
        pass # run before data is written to the database
    def after_update(self):
        pass # run before data is written to the database
    def after_delete(self):
        pass # run before data is written to the database

Base = declarative_base(cls=MyBase)