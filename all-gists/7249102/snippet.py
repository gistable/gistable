from sqlalchemy.engine import create_engine
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.orm.session import sessionmaker


class SQLAlchemy:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if not hasattr(app, 'extensions'):
            app.extensions = {}

        app.extensions['sqlalchemy'] = self
        pool_size = app.config.get('SQLALCHEMY_POOL_SIZE', 5)
        max_overflow = app.config.get('SQLALCHEMY_MAX_OVERFLOW', 15)

        self.engine = create_engine(app.config['SQLALCHEMY_URL'], pool_size=pool_size, max_overflow=max_overflow)
        self.session = scoped_session(sessionmaker(self.engine))
        app.teardown_appcontext(self.close_session)

    def close_session(self, response_or_exc):
        try:
            if response_or_exc is None and self.session.is_active:
                self.session.commit()
        finally:
            self.session.remove()

        return response_or_exc