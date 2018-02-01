import os
from fabric.api import env, require, run, sudo, cd

env.project_name = ''
env.server_name = ''
env.webapps_root = '/opt/webapps/'

env.project_root = os.path.join(env.webapps_root, env.project_name)
env.activate_script = os.path.join(env.project_root, 'env/bin/activate')
env.wsgi_file = os.path.join(env.project_root, 'django.wsgi')
env.repo_root = os.path.join(env.project_root, 'repository')
env.search_index = os.path.join(env.project_root, 'search_index')
env.requirements_file = os.path.join(env.repo_root, 'requirements.txt')
env.manage_dir = os.path.join(env.repo_root, env.project_name)

def production():
    env.hosts = [env.server_name]
prod = production

def virtualenv(command, use_sudo=False):
    if use_sudo:
        func = sudo
    else:
        func = run
    func('source "%s" && %s' % (env.activate_script, command))

def update():
    require('hosts', provided_by=[production])
    with cd(env.repo_root):
        run('git pull origin master')

def install_requirements():
    require('hosts', provided_by=[production])
    virtualenv('pip install -q -r %(requirements_file)s' % env)

def manage_py(command, use_sudo=False):
    require('hosts', provided_by=[production])
    with cd(env.manage_dir):
        virtualenv('python manage.py %s' % command, use_sudo)

def syncdb(app=None):
    require('hosts', provided_by=[production])
    manage_py('syncdb --noinput')

def migrate():
    require('hosts', provided_by=[production])
    manage_py('migrate')

def rebuild_index():
    require('hosts', provided_by=[production])
    manage_py('rebuild_index --noinput', use_sudo=True)
    sudo('chown -R www-data:www-data %(search_index)s' % env)

def collectstatic():
    require('hosts', provided_by=[production])
    manage_py('collectstatic -l --noinput')

def reload():
    require('hosts', provided_by=[production])
    sudo('supervisorctl status | grep %(project_name)s '
         '| sed "s/.*[pid ]\([0-9]\+\)\,.*/\\1/" '
         '| xargs kill -HUP' % env)

def deploy():
    require('hosts', provided_by=[production])
    update()
    install_requirements()
    syncdb()
    migrate()
    collectstatic()
    reload()