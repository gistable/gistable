#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Fabric 0.9/1.x – Synchronize files in a project folder with webserver

from fabric.api import env
from fabric.contrib.project import rsync_project

env.hosts = ['domain.com']
env.path = '/home/user/project/'

def sync():
    """
    Synchronize project with webserver
    """
    rsync_project(env.path, delete=True, exclude=['*.pyc','*.py','.DS_Store'])