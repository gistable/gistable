import os
import sys

from fabric.api import cd, env, lcd, local, parallel, roles, run
from fabric.context_managers import settings
from fabric.contrib.console import confirm
from fabric.decorators import runs_once

env.use_ssh_config = True

env.roledefs.update({
    'webserver': ['server1', 'server2'],
})


def make_envs_command():
    envs = [
        'RDS_DB_NAME=dbname',
        'RDS_DB_USER=dbuser',
        'RDS_DB_PASSWORD=dbpassword',
        'RDS_DB_HOST=dbhost',
    ]
    return ' '.join(map('-e {}'.format, envs))


@roles('webserver')
def deploy():
    rebuild()
    pull()
    migrate()
    restart()


@roles('webserver')
@runs_once
def rebuild():
    local('docker build -t docker_image .')
    local('docker push docker_image')


@roles('webserver')
@parallel
def pull():
    run('docker pull docker_image')


@roles('webserver')
@runs_once
def migrate():
    run('docker run --rm -t {} docker_image python manage.py migrate'.format(make_envs_command()))


@roles('webserver')
def restart():
    with settings(warn_only=True):
        run('docker stop web')
        run('docker rm web')
    run('docker run --name web {} -p 8000:8000 -d docker_image'.format(make_envs_command()))
