# In myapp.tasks __init__.py

from celery import Celery
celery = Celery()
Task = celery.create_task_cls()

class MyBaseTask(Task):
    abstract = True
    # ...

# In myapp.tasks add.py

from myapp.tasks import celery, MyBaseTask

@celery.task(base=MyBaseTask)
def add(x, y):
    return x + y

# In myapp __init__.py

import sys
from myapp.config import valid_configs
from myapp.models import init_model

def create_app(env):
    app = Flask(__name__)
    # This is just my convention for Flask, have a registry of configs
    # so you don't have to store them all in one place, which might be in source
    config = valid_configs.get(env)
    if not config:
        sys.exit('Invalid config, choices are [%s]' % ','.join(valid.configs.keys()))

    app.config.from_object(config)

    # Borrowed from Pylons, sets up connections, etc. but might do some broker setup in relation to celery
    init_model(app)

    # Celery: here's the magic part that you couldn't do before
    # Assuming the config for your particular env has the celery stuff
    from myapp.tasks import celery
    celery.config.from_object(config)

    return app

# In manage.py (or app.py as I usually call it, whatever runs your server)

import sys
from myapp import create_app
from flaskext.script import Manager
from flaskext.celery import install_commands

# Again, this is just something I personally do
# to keep configs and such out of source
env = 'dev'
try:
    env = open('use_env').read().strip()
    if env != 'dev':
        conf_file = env + '_config'
        __import__('myapp.' + conf_file)
except IOError:
    pass

app = create_app(env)
manager = Manager(app)
install_commands(manager)

if __name__ == '__main__':
    manager.run()