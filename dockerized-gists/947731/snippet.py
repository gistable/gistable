#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# written by Arthur Furlan <afurlan@valvim.com>

from __future__ import with_statement

from fabric.api import *
import socket
import time
import os


## environment configuration
env.webserv = 'nginx'
env.project = 'project'
env.gitrepo = 'git@git.example.com:project.git'
env.baseurl = 'example.com'
env.basedir = '/srv/%s/nginx/www/%s/' % (env.baseurl, env.project)
env.projdir = os.path.join(env.basedir, 'src', env.project)
env.owndirs = (
    (os.path.dirname(env.basedir.rstrip('/')), 'git:'),
    (os.path.join(env.projdir, 'media', 'images'), 'www-data:'),
)
env.appdep = (
    ('git@git.example.com:some-app-1.git', os.path.join(env.basedir, '..', 'some-app-1')),
    ('git@git.example.com:some-app-2.git', os.path.join(env.basedir, '..', 'some-app-2')),
)
env.dbuser = 'dbuser'
env.dbname = 'dbname'

## utilities and wrappers

def _wrapper_service(service, action, args=''):
    local('/etc/init.d/%s %s %s' % (service, action, args))

def _wrapper_manage(basedir, action, args=''):
    manage = os.path.join(basedir, 'manage.py')
    local('python %s %s %s' % (manage, action, args))

def _wrapper_setup(basedir, action, args=''):
    os.chdir(basedir)
    local('python setup.py %s %s' % (action, args))

def _service_restart(service, args=''):
    _wrapper_service(service, 'restart', args)

def _service_reload(service, args=''):
    _wrapper_service(service, 'reload', args)

def _restart_gunicorn():
    _service_restart('gunicorn_django', env.project)

def _restart_webserver(restart=True):
    if not restart:
        _service_restart(env.webserv)
    else:
        _service_reload(env.webserv)

def _restart_memcached():
    _service_restart('memcached')

def _git_pull(basedir, repo, version=None, remote='origin', branch='master'):
    if not os.path.exists(basedir):
        _git_clone(basedir, repo)

    os.chdir(basedir)
    local('su git -c "git pull %s %s"' % (remote, branch))

    if version:
        local('su git -c "git checkout %s"' % version)

def _git_clone(basedir, repo):
        local('su git -c "git clone %s %s"' % (repo, basedir))

def _setup_directories(create_parent=True):
    if create_parent:
        parent = os.path.dirname(env.basedir.rstrip('/'))
        if not os.path.exists(parent):
            os.makedirs(parent)

    for path, owner in env.owndirs:
        path = os.path.join(env.basedir, path)
        if os.path.exists(path):
            local('chown -R %s %s' % (owner, path))

def _setup_database():
    output = local('su postgres -c "psql --list -tA"')
    exists = False

    for line in output.split('\n'):
        try:
            values = line.split('|')
        except ValueError:
            continue
        exists |= (values[0] == env.dbname)

    if not exists:
        with settings(warn_only=True):
            local('su postgres -c "createuser -SDR %s"' % dbuser)
            local('su postgres -c "createdb %s -O %s -E UTF8"' % (dbname, dbuser))
    
def _deploy_repo(version=None):
    _git_pull(env.basedir, env.gitrepo, version=version)

def _deploy_apps():
    for apprepo, appdir in env.appdep:
        _git_pull(appdir, apprepo)
        _wrapper_setup(appdir, 'install')

def _deploy_syncdb():
    _wrapper_manage(env.projdir, 'syncdb', '--noinput')

def _deploy_migrate():
    _wrapper_manage(env.projdir, 'migrate')

def _enable_site(siteconf):
    workconf = os.path.join('/etc', env.webserv, 'sites-enabled', env.baseurl)
    os.unlink(workconf)
    os.symlink(siteconf, workconf)


## configured commands for fabric

def setup():
    _setup_directories()
    _setup_database()

def deploy(version=None):
    _deploy_repo(version)
    _deploy_apps()
    _deploy_syncdb()
    _deploy_migrate()
    restart()

def restart(webserver=False, memcached=False, restart=True):
    _restart_gunicorn()
    if webserver:
        _restart_webserver(restart)
    if memcached:
        _restart_memcached()

def maintenance(status):
    wservdir = os.path.join('/etc', env.webserv)
    siteconf = os.path.join(wservdir, 'sites-available', env.baseurl)
    if status == 'on':
        siteconf += '-maintenance'

    _enable_site(siteconf)
    _restart_webserver()