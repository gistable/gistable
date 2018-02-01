#!/usr/bin/env python
# encoding: utf-8
"""
Usage:
    fab deploy:appname
"""
from fabric.api import env, run, cd, local, put

env.hosts = ['myserver.com']
env.user = 'eric'
DEPLOY_PATH = '/var/www/'
APP_NAME = None
APP_PATH = None
DATABASE_CONF_PATH = '/srv/conf/database.yml'

def pack_code():
    local('svn export --force svn://192.168.1.5/projects/%s /tmp/%s'%(APP_NAME,APP_NAME))
    with cd('/tmp/%s'%APP_NAME):
        local('tar czf /tmp/%s.tgz .'%APP_NAME)

def upload_code():
    put('/tmp/%s.tgz'%APP_NAME, '/tmp/')
    with cd(APP_PATH):
        run('tar xzf /tmp/%s.tgz'%APP_NAME)

def conf():
    run("cp %s %s/config/"%(DATABASE_CONF_PATH, APP_PATH))
    run("ln -nfs /srv/photos %s/public/photos"%APP_PATH)
    with cd(APP_PATH):
        run("rake db:migrate RAILS_ENV=production")

def restart(name='back-end'):
    run("touch %s%s/tmp/restart.txt"%(DEPLOY_PATH, name))

def deploy(name='back-end'):
    global APP_NAME, APP_PATH
    APP_NAME = name
    APP_PATH = '%s%s'%(DEPLOY_PATH, APP_NAME)
    pack_code()
    upload_code()
    conf()
    restart(APP_NAME)