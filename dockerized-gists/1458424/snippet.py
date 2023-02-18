from __future__ import with_statement
from datetime import datetime
from sys import exit
from fabric.api import env, run, local, task, settings, sudo
import re

env.hosts = ['www-data@grahamweldon.com']

environments = {
	'__base__': {
		'default': False,
		'repository_uri': 'git@github.com:predominant/grahamweldon.com.git',
		'current_dir': 'current',
		'config_dir': 'config',
		'configs': [
			'Config/database.php',
			'Config/bootstrap.php',
			'Config/core.php',
		],
		'delete': [
			'webroot/uploads',
			'Config/bootstrap.php',
			'webroot/test.php',
		],
		'link': {
			'uploads': 'webroot/uploads'
		}
	},
	'production': {
		'branch': 'main',
		'site_dir': '/var/sites/grahamweldon.com/'
	},
	'stage': {
		'branch': 'develop',
		'site_dir': '/var/sites/stage.grahamweldon.com/',
		'default': True
	}
}

timestr = ''
deployconf = {}

@task(default=True)
def deploy(environment=None):
	global deployconf, timestr
	timestr = run('date +%Y%m%d.%H%M').strip()
	envs = init_environments(environments)
	deployconf = envs[get_environment(environment, envs)]

	clone()
	delete()
	config()
	links()
	current_link()
	services()

@task
def clone():
	arun('git clone {0} {1}{2}'.format(deployconf['repository_uri'], deployconf['site_dir'], timestr))
	arun('(cd {0}{1} && git submodule update --init --recursive)'.format(deployconf['site_dir'], timestr))
	# run('git checkout -b {0} origin/{0}'.format(branch))

@task
def config():
	for f in deployconf['configs']:
		run('ln -s {0}{1}/{2} {0}{3}/{2}'.format(deployconf['site_dir'], deployconf['config_dir'], f, timestr))

@task
def delete():
	for f in deployconf['delete']:
		run('rm -rf {0}{1}/{2}'.format(deployconf['site_dir'], timestr, f))

@task
def links():
	for k, v in deployconf['link'].iteritems():
		if (re.match('^\/.*', k)):
			# Absolute path
			run('ln -s {0} {1}{2}/{3}'.format(k, deployconf['site_dir'], timestr, v))
		else:
			# Relative path
			run('ln -s {0}{1} {0}{2}/{3}'.format(deployconf['site_dir'], k, timestr, v))
	
@task
def current_link():
	run('rm {0}{1}'.format(deployconf['site_dir'], deployconf['current_dir']))
	run('ln -s {0}{1} {0}{2}'.format(deployconf['site_dir'], timestr, deployconf['current_dir']))

@task
def services():
	run('apc-clear');
	sudo('service php5-fpm restart');

def arun(cmd):
	"""
	Alias run command to do SSH Agent forwarding
	This just passes through the ssh client, with the -A option to allow ssh agent forwarding.
	"""
	for h in env.hosts:
		try:
			host, port = h.split(':')
			local('ssh -p %s -A %s "%s"' % (port, host, cmd))
		except ValueError:
			local('ssh -A %s "%s"' % (h, cmd))

def init_environments(environments):
	"""
	Do a merge of the environment settings on top of the __base__ configuration
	"""
	for k, v in environments.iteritems():
		if k is not '__base__':
			environments[k] = dict(environments['__base__'], **v)
	return environments

def get_environment(name, environments):
	if name is not None:
		return name
	for name, s in environments.iteritems():
		if name is not '__base__' and s['default'] is True:
			return name

	print 'You fail so hard. You need to configure a default environment, or specify one like so:'
	print '   $ fab deploy:environment=production'
	exit(1)
