from fabric.api import *
import os
import fabric.contrib.project as project

# Local path configuration (can be absolute or relative to fabfile)
env.theme = 'themes/your-theme'
env.deploy_path = '/absolute/path/for/generated/output'

# Remote server configuration
prod = 'username@server.example.com:22'
dest_path = '/home/username/web/yoursite/'

DEPLOY_PATH = env.deploy_path

def clean():
    if os.path.isdir(DEPLOY_PATH):
        local('rm -rf {deploy_path}'.format(**env))

def gen():
    local('pelican -t {theme} -s local.py'.format(**env))

def serve():
    local('cd {deploy_path} && python -m SimpleHTTPServer'.format(**env))

def reserve():
    gen()
    serve()

def preview():
    local('pelican -t {theme} -s production.py'.format(**env))

@hosts(prod)
def publish():
    local('pelican -t {theme} -s production.py'.format(**env))
    project.rsync_project(
        remote_dir=dest_path.rstrip('/') + '/',
        local_dir=DEPLOY_PATH.rstrip('/') + '/',
        delete=True
    )
    clean()