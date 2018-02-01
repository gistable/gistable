from fabric.api import local, run, env, put
import os, time

# remote ssh credentials
env.hosts = ['10.1.1.25']
env.user = 'deploy'
env.password = 'XXXXXXXX' #ssh password for user
# or, specify path to server public key here:
# env.key_filename = ''

# specify path to files being deployed
env.archive_source = '.'

# archive name, arbitrary, and only for transport
env.archive_name = 'release'

# specify path to deploy root dir - you need to create this
env.deploy_project_root = '/var/www/projectx/'

# specify name of dir that will hold all deployed code
env.deploy_release_dir = 'releases'

# symlink name. Full path to deployed code is env.deploy_project_root + this
env.deploy_current_dir = 'current'

def update_local_copy():
	# get latest / desired tag from your version control system
	print('updating local copy...')

def upload_archive():
	# create archive from env.archive_source
	print('creating archive...')
	local('cd %s && zip -qr %s.zip -x=fabfile.py -x=fabfile.pyc *' \
		% (env.archive_source, env.archive_name))

	# create time named dir in deploy dir
	print('uploading archive...')
	deploy_timestring = time.strftime("%Y%m%d%H%M%S")
	run('cd %s && mkdir %s' % (env.deploy_project_root + \
		env.deploy_release_dir, deploy_timestring))

	# extract code into dir
	print('extracting code...')
	env.deploy_full_path = env.deploy_project_root + \
		env.deploy_release_dir + '/' + deploy_timestring
	put(env.archive_name+'.zip', env.deploy_full_path)
	run('cd %s && unzip -q %s.zip -d . && rm %s.zip' \
		% (env.deploy_full_path, env.archive_name, env.archive_name))

def before_symlink():
	# code is uploaded, but not live. Perform final pre-deploy tasks here
	print('before symlink tasks...')

def make_symlink():
	# delete existing symlink & replace with symlink to deploy_timestring dir
	print('creating symlink to uploaded code...')
	run('rm -f %s' % env.deploy_project_root + env.deploy_current_dir)
	run('ln -s %s %s' % (env.deploy_full_path, env.deploy_project_root + \
		env.deploy_current_dir))

def after_symlink():
	# code is live, perform any post-deploy tasks here
	print('after symlink tasks...')

def cleanup():
	# remove any artifacts of the deploy process
	print('cleanup...')
	local('rm -rf %s.zip' % env.archive_name)

def deploy():
	update_local_copy()
	upload_archive()
	before_symlink()
	make_symlink()
	after_symlink()
	cleanup()
	print('deploy complete!')