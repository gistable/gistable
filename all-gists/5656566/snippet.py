from fabric.api import task, local, sudo, run, prefix, env, cd
from fabric.contrib.files import exists, first
from contextlib import contextmanager, nested

def once(s):
    """Command_prefixes is a list of prefixes"""
    if s not in env.command_prefixes:
        return s
    return 'true'


@contextmanager
def vwrap():
    """Activates virtualenvwrapper commands"""
    # This are the virtualenvwrapper shell aliases file location 
    # if installed via:
    # apt-get install virtualenvwrapper or pip install virtualenvwrapper
    shfile = first('/etc/bash_completion.d/virtualenvwrapper',
                   '/usr/local/bin/virtualenvwrapper.sh')
    with prefix(once('source %s' % shfile)):
        yield



@contextmanager
def virtualenv():
    """Subsequent commands run within the virtual environment"""
    with nested(vwrap(), prefix(once('workon %s' % env.project_name))):
        yield


@contextmanager
def cd_project_path():
    """Cd one folder above the src folder"""
    with cd(env.project_path):
        yield


@contextmanager
def cd_src_path():
    """Cd inside the src folder"""
    with cd(env.src_path):
        yield


def mkvirtualenv():
    """Just create a virtual enviroment"""
    with vwrap():
        run('mkvirtualenv %(project_name)s' % env)


def add_user(user, sudoer=False):
    with settings(warn_only=True):
        result = sudo('useradd -m %s' % (user))
    if not result.failed:
        if sudoer:
            sudo('echo "%s ALL=(ALL) ALL" >> /etc/sudoers' % user)
        password = generate_password()
        sudo('echo "%s:%s" | chpasswd' % (user, password))
        return password
    return False


def git_update():
    # Clone the repo, and if it already exists ignore the error
    if not exists(env.src_path):
        with cd_project_path():
            run('git clone %(repo)s' % env)

    # Fast-foward from origin main
    with cd_src_path():
        run('git pull origin main')


@task
def install_requirements():
     """Install requirements.txt packages using pip"""
     with nested(virtualenv(), cd_src_path()):
         run('pip install -r requirements.txt')


def removepyc():
     """Remove pyc files since they can keep old code alive"""
     with cd_src_path():
         run('find -name "*.pyc" -delete')

