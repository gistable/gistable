
session_engines = {}


def get_new_session(connection=None, autocommit=None):
    connection = connection or 'default'
    connection_settings = settings.DATABASES[connection]
    connection_autocommit = ValueUtils.none_or(
        connection_settings.get('autocommit'), False)
    autocommit = ValueUtils.none_or(autocommit, connection_autocommit)
    session_key = connection + str(int(autocommit))
    try:
        Session = session_engines[session_key]
    except KeyError:
        engine_url = get_engine_url(connection, autocommit)
        pool_size = connection_settings['pool_size']
        pool_recycle = connection_settings['pool_recycle']
        engine = create_engine(
            engine_url, pool_size=pool_size, pool_recycle=pool_recycle)
        Session = sessionmaker(bind=engine, autocommit=autocommit)
        session_engines[session_key] = Session
    return Session()



def autocommit_scope(using=None):
    """自动提交事务操作装饰器。"""

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            has_classarg = False
            if args:
                funcattr = getattr(args[0], func.__name__, None)
                if funcattr is not None and hasattr(funcattr, '__self__'):
                    has_classarg = True

            session = get_new_session(connection=using, autocommit=True)
            if has_classarg:
                # 处理类相关方法传参方式
                classarg = args[0]
                args = args[1:]
                return func(classarg, session, *args, **kwargs)
            else:
                return func(session, *args, **kwargs)

        return wrapper

    return decorator
  
  
class Atomic(object):
    """sqlalchemy orm事务上下文管理器。"""

    def __init__(self, session=None, using=None):
        nested = True
        if session is None:
            session = get_new_session(connection=using, autocommit=False)
            nested = False
        self._session = session
        self.nested = nested

    def __enter__(self):
        if self.nested:
            self._session.begin_nested()
        return self._session

    def __exit__(self, type, value, traceback):
        try:
            if type is None:
                try:
                    self._session.commit()
                except:
                    self._session.rollback()
                    raise
                else:
                    self.exit()
            else:
                self._session.rollback()
        finally:
            if not self.nested:
                self._session.close()

    def exit(self):

        transaction_commit_signal.signal()
        transaction_commit_signal.reset()


def transaction_scope(using=None):
    """单个事务管理器装饰器。"""

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            has_classarg = False
            if args:
                funcattr = getattr(args[0], func.__name__, None)
                if funcattr is not None and hasattr(funcattr, '__self__'):
                    has_classarg = True

            with Atomic(using=using) as session:
                if has_classarg:
                    # 处理类相关方法传参方式
                    classarg = args[0]
                    args = args[1:]
                    return func(classarg, session, *args, **kwargs)
                else:
                    return func(session, *args, **kwargs)

        return wrapper

    return decorator

