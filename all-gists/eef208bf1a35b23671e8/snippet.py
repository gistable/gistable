from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm

env.use_ssh_config = True
env.user = 'username'
env.hosts = ['hostname']

release_dir = '/var/www/path/to/website'
remote_context = 'Production'
local_context = 'Development'
site_package_key = 'Vendor.Sitename'
site_package_path = 'Packages/Sites/%s' % site_package_key
repository = 'git@repository'
content_folder = "%s/Resources/Private/Content" % site_package_path

@task
def getSite():
	'''
	Transfers the remote site content to the local instance
	'''
	with cd(release_dir), shell_env(FLOW_CONTEXT=remote_context):
		run("./flow site:export --tidy --package-key %s --filename %s/Sites.xml" % (site_package_key, content_folder))
		local("rm -rf %s/*" % content_folder)
		get(content_folder, "%s/Resources/Private" % site_package_path)

	if prompt("Download finished. Do you want to import the site? [Y/n]", default="y") == "y":
		importSite()

@task
def pushSite():
	'''
	Transfers the local site content to the remote instance
	'''
	exportSite()

	with cd(release_dir), shell_env(FLOW_CONTEXT=remote_context):
		put(content_folder, "%s/Resources/Private" % site_package_path)
		run("./flow site:prune")
		run("./flow site:import --package-key %s" % site_package_key)

@task
def importSite():
	'''
	Prune local site and reimport content
	'''
	with shell_env(FLOW_CONTEXT=local_context):
		local("./flow site:prune")
		local("./flow site:import --package-key %s" % site_package_key)

@task
def exportSite():
	'''
	Exports local content to site package
	'''
	with shell_env(FLOW_CONTEXT=local_context):
		local("./flow site:export --tidy --package-key %s --filename %s" % (site_package_key, content_folder))

@task
def createUser(username, password):
	'''
	Create new user
	'''
	local("./flow typo3.neos:user:create --username=%s --password=%s --first-name=Admin --last-name=Istrator" % (username, password))

@task
def setUserPassword(password, username='admin'):
	'''
	Set a users password
	'''
	local("./flow typo3.neos:user:setpassword --username=%s --password=%s" % (username, password))

@task
def nodeRepair():
	'''
	Run node repair on remote host
	'''
	with cd(release_dir), shell_env(FLOW_CONTEXT=remote_context):
		run("./flow node:repair")

@task
def clearCache():
	'''
	Run cache flush on remote host
	'''
	with cd(release_dir), shell_env(FLOW_CONTEXT=remote_context):
		run("./flow flow:cache:flush")
