from fabric.api import env
from fabric import tasks
from functools import wraps

def _wrap_as_new(original, new):
    if isinstance(original, tasks.Task):
        return tasks.WrappedCallableTask(new)
    return new

def strict_roles(*role_list):
    """
    Extended version of the built-in fabric roles decorator which will
    not run the task if the current host is not found in the roledefs
    for each role assigned to the decorated task.

    Hack to work around this: https://github.com/fabric/fabric/issues/464

    Example:
    
        @strict_roles('apache'):
        def restart_apache():
            fab.sudo('/etc/init.d/apache2 reload')
    """
    def attach_list(func):
        @wraps(func)
        def inner_decorator(*args, **kwargs):
            # Check for the current host in the roledefs for
            # each role the task is restricted to.
            for role in getattr(func, 'roles', []):
                if env.host in env.roledefs.get(role, []):
                    return func(*args, **kwargs)
            # Don't do anything 
            return False
        _values = role_list
        # Allow for single iterable argument as well as *args
        if len(_values) == 1 and not isinstance(_values[0], basestring):
            _values = _values[0]
        setattr(inner_decorator, 'roles', list(_values))
        setattr(func, 'roles', list(_values))
        # Don't replace @task new-style task objects with inner_decorator by
        # itself -- wrap in a new Task object first.
        inner_decorator = _wrap_as_new(func, inner_decorator)
        return inner_decorator
    return attach_list