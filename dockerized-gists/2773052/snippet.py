import sys
from fabric.colors import green, yellow
from fabric.contrib.console import confirm
from fabric.context_managers import cd, prefix
from fabric.operations import prompt
from fabric.api import run, local, env, sudo

env.user = 'ubuntu'
env.hosts = ['0.0.0.0'] #ip do ec2
env.app_path = '/home/seu-usuario-do-ec2/bomgusto'
env.virtualenv_path = '/path/para/seu/virtualenv'
env.pid_path = '/home/seu-usuario-do-ec2/gunicorn.pid'


#deploy for nginx+guncorn is great man....
def start_deploy():
	local('fab -H ubuntu@ip do ec2 deploy_nginx')

def start_bomgusto():
	sys.stdout.write(green(u'Starting the Bomgusto.com'))
	sys.stdout.write('\n')
	with cd(env.app_path):
		sudo('supervisorctl start bomgusto')
	sudo('service nginx start')
	sys.stdout.write(green(u'Bomgusto.com is running...'))

def stop_bomgusto():
	sys.stdout.write(green(u'Stoping Bomgusto.com...'))
	sys.stdout.write('\n')
	result = sudo('supervisorctl stop bomgusto')
	if result.failed:
		sys.stdout.write(yellow(u'Bomgusto is not running'))
		return result
	sys.stdout.write(green(u'Bomgusto.com... stoped'))
	return result


def deploy_nginx():
	result = stop_bomgusto()
	run('source /home/ubuntu/enviroment/bomgusto/bin/activate')
	sys.stdout.write(green(u'Activating of the virtualenv for bomgusto'))
	sys.stdout.write('\n')

	with cd(env.app_path):
		run('git pull origin main')

		if confirm(u"Do u want install new pip's ?"):
			install_requeriments()	

		if confirm(u"Do u want collectstatic ?"):
			run('%sbin/python manage.py collectstatic' % (env.virtualenv_path))

		if confirm(u"Do u have migrates?"):
			update_database()
	
	start_bomgusto()

def update_database():
    with cd(env.app_path):
        run("%sbin/python manage.py syncdb" % (env.virtualenv_path))
        run("%sbin/python manage.py migrate" % (env.virtualenv_path))
    

def install_requirements():
	run("%sbin/pip install -r %srequirements.txt" % (env.virtualenv_path, env.app_path))
