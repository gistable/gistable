import os
import sys

from fabric.api import abort, run, sudo, env, cd
from fabric.colors import red, green
from fabric.contrib.files import exists, put, upload_template

ROOT = '/home/jquick/code/'
WORKON = '/home/jquick/.virtualenvs'
VENVS = {
    'bmore': ('ram','bmoredancehub.org',)
}
OPTIONS = '--debug'

get_pid = lambda v: os.path.join(ROOT, v, '.pid')
get_sock = lambda v: os.path.join(ROOT, v, '.sock')
get_log = lambda v: os.path.join(ROOT, 'logs', v)
env.virtual = None

def workon(virtual_env):
    if not virtual_env in VENVS:
        abort('Unknown virtual environment: %s' % virtual_env)
    env.virtual = virtual_env

def virtual_env_check(func):
    def inner(*args, **kwargs):
        if args and args[0] in VENVS:
            workon(args[0])
            return func(*args[1:], **kwargs)
        return func(*args, **kwargs)
    return inner

@virtual_env_check
def stop():
    pid = get_pid(env.virtual)
    if exists(pid):
        run('kill `cat "%s"`' % pid)
        print green('%s stopped' % env.virtual)
        return
    print red('%s not running' % env.virtual)
    
@virtual_env_check
def start():
    py = os.path.join(WORKON, env.virtual, 'bin', 'python')
    manage = os.path.join(ROOT, env.virtual, 'manage.py')
    debug = ''
    run('%s "%s" run_gunicorn %s -D --pid="%s" --log-file="%s" -b "unix:%s"' % \
        (py, manage, debug, get_pid(env.virtual),
         get_log(env.virtual), get_sock(env.virtual)))
    print green('%s running' % env.virtual)
    
def kill(pid_file, flags=''):
    if not pid_file:
        if not env.virtual:
            abort('Pass a pidfile or define a virtual environment')
        pid_file = get_pid(env.virtual)
    if exists(pid_file):
        run('kill %s `cat %s`' % (flags, pid))
    
    
@virtual_env_check
def workup():
    kill(flags='-TTIN')
    pid = get_pid(env.virtual)
    if exists(pid):
        run('kill -TTIN `cat "%s"`' % pid)
        return
    print red('%s does not seem to be running' % env.virtual)
    
@virtual_env_check
def workdown():
    pid = get_pid(env.virtual)
    if exists(pid):
        run('kill -TTOU `cat "%s"`' % pid)
        return
    print red('%s does not seem to be running' % env.virtual)
    
@virtual_env_check
def restart():
    stop()
    start()
    
@virtual_env_check
def init(url, dest=ROOT):
    if env.virtual:
        run('mkvirtualenv %s' % env.virtual)
    with cd(dest):
        run('git clone %s' % url)

@virtual_env_check
def update():
    with cd(os.path.join(ROOT, env.virtual)):
        run('git reset --hard')

@virtual_env_check
def reqs(f='setup/requirements.txt'):
    pip = os.path.join(WORKON, env.virtual, 'bin', 'pip')
    with cd(os.path.join(ROOT, env.virtual)):
        run('%s install -r %s' % (pip, f))

def service(name, *actions):
    for action in actions:
        sudo('/etc/init.d/%s %s' % (name, action))

def nginx(template_file='nginx-site.conf'):
    conf = os.path.join(ROOT, 'conf')
    for virtual,aliases in VENVS.items():
        vconfig = os.path.join(conf, virtual)
        upload_template(template_file, vconfig, {
            'aliases': ' '.join(aliases),
            'root': os.path.join(ROOT, virtual),
            'sock': get_sock(virtual),
            'virtual': virtual,
        })
    
        dest = '/etc/nginx/sites-enabled/%s' % virtual
        if not exists(dest, True):
            sudo('ln -s "%s" "%s"' % (vconfig, dest))
