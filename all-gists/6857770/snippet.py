# -*- coding: utf-8 -*-
import logging
import os
from os.path import abspath, dirname, join
from os import environ

from fabric.api import env, task
from fabric.operations import local
from fabric.operations import sudo
from fabric.utils import puts
from fabric.colors import green, red
from fabric.api import *
from fabric.context_managers import lcd

BASEDIR = dirname(__file__)
BACKENDDIR = abspath(join(abspath(BASEDIR), 'backend'))
FRONTENDDIR = abspath(join(abspath(BASEDIR), 'frontend'))
LOGGER = logging.getLogger(__name__)

requirements_file = abspath(join(abspath(BACKENDDIR), 'requirements.txt'))


def get_venv():
  """ Get the current virtual environment name
		Bail out if we're not in one
	"""
	try:
		return os.environ['VIRTUAL_ENV']
	except KeyError:
		print 'Not in a virtualenv'
		exit(1)


def get_pip():
	""" Get an absolute path to the pip executable
		for the current virtual environment
	"""
	return join(get_venv(), 'bin', 'pip')

def check_for(what, unrecoverable_msg, installation_cmd=None):
	def failure():
		print unrecoverable_msg
		exit()

	try:
		test_result = local("which %s" % what, capture=True)
		return test_result
	except:
		if(installation_cmd):
			print "Unable to find %s, will attempt installation (you might be asked for sudo password below)"
			local(installation_cmd)
		else:
			failure()
		try:
			test_result = local(cmd, capture=True)
			return test_result
		except:
			failure()

def get_node():
	return check_for('node', 'You need to install Node.js to run the Require.js optimiser and the frontend tests')

def get_npm():
	return check_for('npm', 'You need to install Node.js and npm to run grunt, less, require.js optimiser and the frontend tests')

def get_less():
	return check_for('lessc', 'You need to install LESS complier to be able to compile your LESS files.', 'sudo npm install -g less')

def get_bower():
	return check_for('bower', 'You need to install Bower to be able to install JS libs', 'sudo npm install -g bower')

def get_grunt():
	return check_for('grunt', 'You need to install Grunt to be able to compile front-end JS, stylesheets and run front-end tests', 'sudo npm install -g grunt-cli')

@task
def install_backend_deps():
	""" Install python dependencies from requirements.txt file
	"""
	with lcd(BACKENDDIR):
		cmd = '%(pip)s install -r %(requirements_file)s' % {
			'pip': get_pip(),
			'requirements_file': requirements_file
		}
		local(cmd)

@task
def install_frontend_deps():
	""" install front-end dependencies using npm and bower
	"""

	with lcd(FRONTENDDIR):
		cmd = '%(npm)s install' % {'npm': get_npm()}
		local(cmd)
		cmd = '%(bower)s install' % {'bower': get_bower()}
		local(cmd)

@task
def install_deps():
	install_backend_deps()
	install_frontend_deps()
	print 'Run `fab develop` to get everything ready for development'

@task
def build():
	with lcd(FRONTENDDIR):
		cmd = '%(grunt)s build' % {'grunt': get_grunt()}
		local(cmd)

@task
def develop():
	with lcd(FRONTENDDIR):
		cmd = '%(grunt)s develop' % {'grunt': get_grunt()}
		local(cmd)

@task
def deploy_production():
	pass
	#@TODO: implement task for auto-deployment to production