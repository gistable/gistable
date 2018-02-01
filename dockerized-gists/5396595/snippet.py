from fabric.api import env
from functools import wraps


def get_target_name(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        print("I am in the decorator")
        for key, value in env.project_sites.iteritems():
            for k, v in value.iteritems():
                if v == env.host:
                    print(key)
                    _env_get(key)
        return f(*args, **kwargs)
    return wrapper


@get_target_name
def host_type():
    print("worker running")
    run('uname -s')