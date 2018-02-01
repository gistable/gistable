# Mostly from django-fab-deploy

import os
import sys
from datetime import datetime
from subprocess import Popen, PIPE

import yaml

from fabric.api import env, run, sudo, task
from fabric.context_managers import cd
from fabric.contrib import files


# Initialisation

env.user = 'ubuntu'

d = yaml.safe_load(Popen(['juju','status'],stdout=PIPE).stdout)

services = d.get("services", {})
if services is None:
    sys.exit(0)

env.roledefs = {}
for service in services.items():
    if service is None:
        continue

    units = services.get(service[0], {}).get("units", {})
    if units is None:
        continue

    for unit in units.items():
        if 'public-address' in unit[1].keys():
            env.roledefs.setdefault(service[0], []).append(unit[1]['public-address'])

# helpers

def _config_get():
    conf = Popen('jitsu run-as-hook %s/0 config-get' % (env.roles[0]),shell=True, stdout=PIPE).stdout
    return eval(conf.read())

def _relation_get(relation, relation_type):
    res = Popen('jitsu run-as-hook %s/0 relation-ids %s' % (env.roles[0], relation_type),shell=True, stdout=PIPE).stdout
    rel_id = res.read().strip()

    conf = Popen('jitsu run-as-hook %s/0 relation-get -r %s' % (relation, rel_id),shell=True, stdout=PIPE).stdout
    return eval(conf.read())


# Debian
@task()
def apt_install(packages):
    sudo('apt-get install -y %s' % packages)

@task
def apt_update():
    sudo('apt-get update')

@task
def apt_dist_upgrade():
    sudo('apt-get dist-upgrade -y')

@task
def apt_install_r():
    sudo("apt-get install -y $(cat requirements.apt | tr '\\n' ' '")

@task
def pip_install(packages):
    sudo("pip install %s" % packages)

@task
def pip_install_r():
    sudo("pip install -r requirements.txt")

# Users

@task
def adduser(username):
    sudo('adduser %s --disabled-password --gecos ""' % username)

@task
def ssh_add_key(pub_key_file, username=None):
    with open(os.path.normpath(pub_key_file), 'rt') as f:
        ssh_key = f.read()

    if username is None:
        run('mkdir -p .ssh')
        files.append('.ssh/authorized_keys', ssh_key)
    else:
        run('mkdir -p /home/%s/.ssh' % username)
        files.append('/home/%s/.ssh/authorized_keys' % username, ssh_key)
        run('chown -R %s:%s /home/%s/.ssh' % (username, username, username))


# VCS

@task
def pull():
    conf = _config_get()
    with cd('/srv/%s/' % env.roles[0]):
        if conf['vcs'] is 'bzr':
            run('bzr pull %s' % conf['repos_url'])
        if conf['vcs'] is 'git':
            run('git pull %s' % conf['repos_url'])
        if conf['vcs'] is 'hg':
            run('hg pull -u %s' % conf['repos_url'])
        if conf['vcs'] is 'svn':
            run('svn up %s' % conf['repos_url'])

        delete_pyc()
    reload()


# Gunicorn

@task
def reload():
    sudo('invoke-rc.d gunicorn reload')


# Django

@task
def manage(command):
    run('python manage.py ' + command)

@task
def migrate(params='', do_backup=True):
    if do_backup is True:
        db_backup('before-migrate')
    manage('migrate --noinput %s' % params)

@task
def syncdb(params=''):
    """ Runs syncdb management command. """
    manage('syncdb --noinput %s' % params)

@task
def collectstatic(params=''):
    manage('collectstatic --noinput %s' % params)


# DB

def _get_dump_filename(backup_dir):
    now = datetime.now().strftime('%Y.%m.%d-%H.%M')
    filename = '%s%s.sql' % (backup_dir, now)
    return filename

@task
def db_list():
    run('find /srv/%s/backups/ -name *.gz' % env.roles[0])

@task
def db_backup(name):
    backup_dir = '/srv/%s/backups/%s/' % (env.roles[0], name)
    run('mkdir -p ' + backup_dir)

    conf = _relation_get('postgresql', 'db')
    conf['filename'] = _get_dump_filename(backup_dir)

    if 'port' not in conf.keys(): conf['port'] = '5432'

    cmd = 'PGPASSWORD="%(password)s" pg_dump --username=%(user)s --host=%(host)s --port=%(port)s %(database)s | gzip -3 > %(filename)s.gz' % conf
    run(cmd)

@task
def db_restore(name):
    backup_file = '/srv/%s/backups/%s' % (env.roles[0], name) 

    conf = _relation_get('postgresql', 'db')
    conf['filename'] = backup_file

    if 'port' not in conf.keys(): conf['port'] = '5432'

    cmd = 'gunzip -c %(filename)s | PGPASSWORD="%(password)s" psql --username=%(user)s --host=%(host)s --port=%(port)s %(database)s' % conf
    run(cmd)


# Utils

@task
def delete_pyc():
    """ Deletes *.pyc files from project source dir """
    run("find . -name '*.pyc' -delete")
 