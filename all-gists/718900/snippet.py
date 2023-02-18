"""
Thomas Pelletier's Python deployment script.
MIT Licensed.


We assume that:
    * deploy.py lives in the root of your project.
    * In the same directory, there is a dependencies.txt file, in PIP format.
    * Remote host has a working Python+VENV+PIP environment.
    * You have enough privileges.
    * The project is GIT or Hg versioned.
    * When you login using ssh, you are in /home/user.
    * Only Gunicorn is supported for now.


Some bulk notes:
    * All projects are stored in the same directory (REMOTE_BASE).
    * The gunicorn mainpid is stored in REMOTE_BASE/name/main.pid
"""


from fabric.api import local, run, sudo, env
from fabric.contrib.files import exists
from fabric.context_managers import cd
from os import path
import datetime
import types
import imp


#: Where all your projects live.
REMOTE_BASE = "/var/www/"
#: Where your project lives on your local machine.
CWD = __file__


###############################################################################
# INTERNAL FUNCTIONS
###############################################################################


def _load_config(filename = None):
    """Load a config file and returns it as a dict.
    Taken from the source code of Flask."""
    if filename == None:
        filename = path.join(path.dirname(CWD), 'config.py')

    obj = imp.new_module('config')
    obj.__file__ = filename

    execfile(filename, obj.__dict__)
    conf = {}

    for key in dir(obj):
        if key.isupper():
            conf[key] = getattr(obj, key)
    return conf


def _remote_path(*args):
    return path.join(REMOTE_PROJECT_PATH, *args)


# Compute some information

CONFIG = _load_config()
PROJECT_NAME = CONFIG['PROJECT_NAME']
REMOTE_PROJECT_PATH= path.join(REMOTE_BASE, PROJECT_NAME)


###############################################################################
# SCM MANAGER
###############################################################################

def SCMManager(repo_path=None, scm=None):
    config = _load_config()
    if scm == None:
        scm = config['SCM']

    managers = {
        'hg': HgManager,
        'git': GitManager,
    }

    return managers[scm](repo_path)



class HgManager(object):
    """
    Provides Hg support for SCMManager.
    """

    def __init__(self, repo_path):
        self.repo_path = repo_path

    def init(self):
        run('cd %s && hg init .' % self.repo_path)

    def push(self, remote_repo, branch=''):
        local('hg push ssh://%s/../..%s %s' % (env.host, self.repo_path, branch))

    def up(self):
        run('cd %s && hg up' % self.repo_path)


class GitManager(object):
    """
    Provides Git support for SCMManager
    """

    def init(self, directory):
        # TODO
        raise NotImplemented

    def push(self, remote_repo, branch=''):
        local('git push %s %s' % (remote_repo, branch))

    def up(self):
        # FIXME Not needed.
        pass



###############################################################################
# FABRIC-RUNABLE FUNCTIONS
###############################################################################

def host_type():
    """Return the exact UNIX operating system."""

    run('uname -s')


def virtualenv():
    """Setup a clean virtualenv"""

    with cd(_remote_path('current')):
        run('virtualenv --no-site-packages .')


def dependencies():
    """Install PIP dependencies"""

    with cd(_remote_path('current')):
        run('pip install -E ./ -r application/dependencies.txt')


def deploy():
    """Update the remote application code."""

    # Load the configuration
    conf = _load_config()

    # Instantiate the SCM
    scm = SCMManager(_remote_path('current', 'application'))

    # Compute the instance name based on the current date + time
    instance_name = datetime.datetime.now().strftime("%Y%m%d%H%M")

    # Check if the remote directory already exists
    if not exists(_remote_path(instance_name, 'application')):
        run('mkdir -p %s' % _remote_path('run'))
        run('mkdir -p %s' % _remote_path(instance_name, 'application'))

    # Create a symlink to the current revision
    run('rm -f %s' % _remote_path('current'))
    run('ln -s %s %s' % (_remote_path(instance_name), _remote_path('current')))

    if not exists(_remote_path('current', 'application', '.hg')):
        scm.init()
    
    if not exists(_remote_path('current', 'bin', 'python')):
        virtualenv()

    # We can now push the new version
    scm.push('production')
    scm.up() # check we are at the correct version

    # Install / Update system dependencies
    dependencies()

    # Restart Gunicorn (or start if it is not running).
    restart()


def restart():
    """Restart the application (gunicorn only for now)."""

    with cd(_remote_path()):
        if not exists(_remote_path('run', 'main.pid')):
            start()
        else:
            run('kill -HUP `cat run/main.pid`')


def stop():
    """Stop the running Gunicorn application."""

    with cd(_remote_path()):
        run('kill -9 `cat run/main.pid`')
        run('rm -f run/main.pid')


def start():
    """Start the Gunicorn application."""
    
    command = '../bin/gunicorn '

    if 'GUNICORN_CONFIG' in CONFIG.keys():
        command += '-c %s' % CONFIG['GUNICORN_CONFIG']
    else:
        command += '-D -p %s -b unix:%s --log-file %s --log-level warning' %\
                (_remote_path('run', 'main.pid'),
                 _remote_path('run', 'app.socket'),
                 _remote_path('run', 'gunicorn_log'))

    if 'GUNICORN_APP' in CONFIG.keys():
        command += ' %s' % CONFIG['GUNICORN_APP']
    else:
        command += ' app:app'

    with cd(_remote_path('current', 'application')):
        # TODO Add settings for app:app
        run('source ../bin/activate')
        run(command)
