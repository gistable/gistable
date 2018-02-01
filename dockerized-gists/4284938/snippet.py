from fabric.api import cd, env, local, prefix, run, sudo

env.hosts = ['cs01.actalis.vpn']
env.project_root = '/home/libersoft/visalaid'
env.user = 'libersoft'


def push():
    local('git push')


def collect_static():
    with prefix('source venv/bin/activate'):
        run('python manage.py collectstatic -v0 --noinput')


def pull():
    with cd(env.project_root):
        run('git pull')
        collect_static()


def reload():
    sudo('supervisorctl restart visalaid', shell=False)


def deploy():
    push()
    pull()
    reload()