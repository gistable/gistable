from contextlib import contextmanager

"""
Usage:

with env_var('MY_VAR', 'foo'):
    # is set here
    
# does not exist here
"""

@contextmanager
def env_var(key, value):
    os.environ[key] = value
    yield
    del os.environ[key]