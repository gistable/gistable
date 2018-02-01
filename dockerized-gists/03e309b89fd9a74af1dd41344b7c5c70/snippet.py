import json
import time
from fabric.api import *
from fabric.contrib.console import confirm

HOOK_URL = 'https://hooks.slack.com/services/XXXXXXXX/XXXXXX/XXXXXXXXXX'
env.key_filename = '/path/to/home/dir/.ssh/id_rsa'
branch = 'development'
code_dir = '/path/to/code/dir'
environment = 'development'


def development():
    env.hosts = ['abc.de.fgh.ijk']
    env.user = 'xxxxxxxx'


def production():
    env.hosts = ['xx.yyy.zzz.qqq']
    env.user = 'xxxxxxx'
    global branch
    branch = 'master'
    global environment
    environment = 'production'


def deploy():
    report('connected with user `' + env.user + '` to the following server...... \n')
    run('uname -a')
    with hide('output'):
        if not confirm('do you want to proceed with deployment to this server?'):
            abort('deployment aborted by user')

        report('Deployment to ' + environment + ' starting.....', True)
        backup_branch = 'backup_' + str(time.time())
        with cd(code_dir):
            remove_old_backup_branches()
            copy_env_vars()
            perform_git_tasks(backup_branch)
            install_requirements()

            test_failed = False
            if environment == 'development':
                test_failed = run_tests()
                if test_failed:
                    report('test failed! rolling back to previous code base', True)
                    run('git checkout ' + backup_branch)

            if not test_failed:
                delete_pyc_files()
                stop_and_start_service()
                report('Deployment to ' + environment + ' was successful!', True)


def run_tests():
    with settings(warn_only=True):
        report('running tests......')
        test = run('./tests.py')
        return test.failed


def copy_env_vars():
    report('installing environment variables.....')
    put(environment + '_secrets.env', code_dir + '/secrets.env')


def install_requirements():
    report('installing requirements....')
    run('flask/bin/pip install -r requirements.txt')


def delete_pyc_files():
    report('deleting pre-compiled files.....')
    run('rm *.pyc')
    run('rm application/*.pyc')


def stop_and_start_service():
    report('stopping fileservice......')
    run('sudo systemctl stop fileservice')

    report('starting fileservice......')
    run('sudo systemctl start fileservice')


def perform_git_tasks(backup_branch):
    report('backing up current branch.....')
    run('git checkout -b ' + backup_branch)

    report('switching back to branch ' + branch + ' ....')
    run('git checkout ' + branch)

    report('pulling from git repository....')
    run('git fetch --all')
    run('git reset --hard origin/' + branch)


def report(message, to_slack=False):
    print message
    if to_slack:
        post_to_slack(message)


def post_to_slack(message):
    if environment == 'production':
        local("curl -X POST -H 'Content-type: application/json' --data '" + json.dumps(
            {'text': message}) + "' " + HOOK_URL)


def remove_old_backup_branches():
    with settings(warn_only=True):
        # delete all branches that have backup in them
        run('git branch -D `git branch | grep "backup"`')
