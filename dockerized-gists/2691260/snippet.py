from fabric.api import *
from fabric.colors import green, red
import os, sys

packages_dir = 'packages'
tmp_dir = 'tmp'
dependencies_filename = 'dependencies.zip'

def check_requirement(command,install_text):
    failed = False
    with settings(warn_only=True):
        if not local('which %s' % command,capture=True):
            print red(install_text)
            failed = True
    if failed:
        abort("Fix dependencies and try again")

def compile_css():
    check_requirement('lessc','No "lessc" found. Install it with "npm install less@latest -g".')
    local('lessc -x static/css/styles.less > static/css/style.css')
    
def precommit():
    compile_css()

def serve():
    local('python app.py')

def package_dependencies():
    'Put all dependencies into one zip for convenience.'
    local('rm -rf %s' % tmp_dir)
    local('mkdir %s' % tmp_dir)
    local('pip install -r requirements.txt -t %s' % tmp_dir)
    local('cd %s && zip %s -r * && cd ..' % (tmp_dir,dependencies_filename))
    local('mkdir -p %s' % packages_dir)
    local('cp %s/%s %s' % (tmp_dir,dependencies_filename,packages_dir))
    local('rm -r %s' % tmp_dir)

def deploy():
    'Google App Engine deploy'    
    if not os.path.exists(packages_dir):
        package_dependencies()
        
    # upload to app engine
    check_requirement('appcfg.py','No "appcfg.py" found. Install it from google: https://developers.google.com/appengine/docs/python/gettingstarted/uploading')
    local('appcfg.py update .')
