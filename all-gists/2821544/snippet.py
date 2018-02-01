# -*- coding: utf-8 -*-

import os
import time
import settings
from fabric.contrib.console import confirm

from fabric.api import local, settings as fabric_settings, env, cd, run, sudo

env.hosts = ['domain_or_ip']
env.user = 'user'
env.path = '/home/user/webapps/project_name'

def start():
    sudo('/etc/init.d/nginx start')

def deploy():
    update_code()
    with cd(env.app_path):
        run("python manage.py collectstatic --noinput")

    update_database()
    start()

def update_code():
    with cd(env.app_path):
        run("git pull")

def update_database():
    with cd(env.path):
        run("python manage.py syncdb")

def restart_nginx():
    sudo('/etc/init.d/nginx restart')