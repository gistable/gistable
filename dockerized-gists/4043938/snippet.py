from __future__ import with_statement
from fabric.api import *
from fabric.contrib.files import exists


env.use_ssh_config = True
env.hosts = ['locum']
REPO = 'git/sapegin.git'
DEST = 'projects/sapegin'


@task(default=True)
def deploy():
	with cd(DEST):
		run('git checkout master')
		run('git pull')
		run('grunt deploy')


@task
def upgrade():
	with cd(DEST):
		run('git checkout master')
		run('git pull')
		run('npm update npm -g')
		run('npm update grunt -g')
		run('npm update')
		with cd('gatherer'):
			run('npm update')


@task
def setup():
	setup_bare()
	setup_clone()
	upgrade()


def setup_bare():
	if exists(REPO + '/config'):
		return
	run('mkdir -p %s' % REPO)
	with cd(REPO):
		run('git --bare init')
		run('git config core.sharedrepository 1')
		run('git config receive.denyNonFastforwards true')
	remote = 'ssh://%s@%s/~/%s' % (env['user'], env['host'], REPO)
	local('git remote add origin %s' % remote)
	local('git push -u origin master')


def setup_clone():
	run('mkdir -p %s' % DEST)
	with cd(DEST):
		run('git clone ~/%s .' % REPO)
