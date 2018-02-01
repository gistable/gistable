from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


# Simple database and session wrapper. I use it in my Flask app too.
class Database(object):
    def __init__(self):
        self.session_maker = sessionmaker()
        self.session = scoped_session(self.session_maker)
        self.engine = None

    def init(self, url, echo):
        self.engine = create_engine(url, echo=echo)
        self.session_maker.configure(bind=self.engine)

    def close_session(self):
        try:
            db.session.commit()
        except:
            db.session.rollback()
        db.session.remove()


db = Database()


# Scoped query, wrap your queries around it
class ScopedQuery(object):
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        db.close_session()

# Before you start your IOLoop, initialize db:
db.init(settings.SQLALCHEMY_DATABASE_URI, echo=settings.SQLALCHEMY_ECHO)

# And now you can make SQLAlchemy queries:
def get_user_name(user_id):
    with ScopedQuery():
        user = db.session.query(models.User).get(user_id)

        if user is None:
            return None

        return user.login

# Obviously, they're synchronous, but you can use separate thread with a callback, etc.
# If you return models, make sure you detach them before attempting to access their properties or do eager loading. 
# For example:
def get_run(run_id):
    with ScopedQuery():
        run = (db.session.query(models.Run)
                .options(joinedload(models.Run.scheduled_run))
                .get(run_id))

        if run is None:
            return None

        db.session.expunge(run)
        db.session.expunge(run.scheduled_run)

        return run
