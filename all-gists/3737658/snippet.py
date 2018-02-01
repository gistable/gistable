from fabric.api import *
from fabric.colors import green

env.hosts = ['my_user@my_host']
env.password = 'my_password'
env.app_path = 'my/app/path'

def commit():
    print(green("Commit last modifs..."))
    local('git add -A && git commit')

def pushpull():
    with cd(env.app_path):
        print(green("Pushing to the ref..."))
        local('git push')
        print(green("Pulling to the Prod..."))
        run('git pull')

def colstat():
    print(green("Prod Collecting Static Files..."))
    with cd(env.app_path):
        run('php app/console assets:install web --symlink')

def cacheclear():
    print(green("Prod Clearing Cache..."))
    with cd(env.app_path):
        sudo('php app/console cache:clear --env=prod', user='www-data')

def httpdrst():  
    print(green("Prod Restarting Apache..."))
    sudo('apache2ctl restart')

def deploy():
    pushpull()
    colstat()
    cacheclear()
#    syncdb()
#    httpdrst()
