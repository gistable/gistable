from sqlalchemy.inspection import inspect

def changed_columns(obj):
    info = inspect(obj)
    return dict((name, attr.history) for name, attr
        in info.attrs.items() if attr.history.has_changes())
