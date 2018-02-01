from sqlalchemy import create_engine, event, orm
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session as SessionBase, object_session
from sqlalchemy.event.api import listen

# The following adds delete, insert, and update events after successful commits.
# SQLAlchemy provides only events after flushes, but not after commits.
# The classes are adapted from Flask-SQLAlchemy.
# see also https://stackoverflow.com/a/12026787/60982

class SignallingSession(SessionBase):
    def __init__(self, **options):
        self._model_changes = {}
        SessionBase.__init__(self, **options)

class _SessionSignalEvents(object):

    def register(self):
        listen(SessionBase, 'after_commit', self.session_signal_after_commit)
        listen(SessionBase, 'after_rollback', self.session_signal_after_rollback)

    @staticmethod
    def session_signal_after_commit(session):
        if not isinstance(session, SignallingSession):
            return
        d = session._model_changes
        if d:
            for obj, change in d.values():
                if change == 'delete' and hasattr(obj, '__commit_delete__'):
                    obj.__commit_delete__()
                elif change == 'insert' and hasattr(obj, '__commit_insert__'):
                    obj.__commit_insert__()
                elif change == 'update' and hasattr(obj, '__commit_update__'):
                    obj.__commit_update__()    
            d.clear()

    @staticmethod
    def session_signal_after_rollback(session):
        if not isinstance(session, SignallingSession):
            return
        d = session._model_changes
        if d:
            d.clear()
            
class _MapperSignalEvents(object):

    def __init__(self, mapper):
        self.mapper = mapper

    def register(self):
        listen(self.mapper, 'after_delete', self.mapper_signal_after_delete)
        listen(self.mapper, 'after_insert', self.mapper_signal_after_insert)
        listen(self.mapper, 'after_update', self.mapper_signal_after_update)

    def mapper_signal_after_delete(self, mapper, connection, target):
        self._record(mapper, target, 'delete')

    def mapper_signal_after_insert(self, mapper, connection, target):
        self._record(mapper, target, 'insert')

    def mapper_signal_after_update(self, mapper, connection, target):
        self._record(mapper, target, 'update')

    @staticmethod
    def _record(mapper, target, operation):
        s = object_session(target)
        if isinstance(s, SignallingSession):
            pk = tuple(mapper.primary_key_from_instance(target))
            s._model_changes[pk] = (target, operation)

# Usage

# this must happen only once
_MapperSignalEvents(orm.mapper).register()
_SessionSignalEvents().register()

# use SignallingSession as session class
engine = create_engine(...)
Session = sessionmaker(bind=engine, class_=SignallingSession)()
