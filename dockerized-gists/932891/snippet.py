"""
Distributor ID: Ubuntu
Description:    Ubuntu 10.04 LTS
Release:        10.04
Codename:       lucid
Author:         Adelein Rodriguez, adeleinr@gmail.com
Note:           This is an adaptation from a fabric script presented here:
                http://morethanseven.net/2009/07/27/fabric-django-git-apache-mod_wsgi-virtualenv-and-p.html

Summary:     This script: 
             1) Installs all linux and python packages FROM SCRATCH needed to get your Django project
                up and running in an Ubuntu remote server. 
             2) Or deploys your local changes to the existing code version in the remote server

Description: This script requires that you have fabric installed => (http://docs.fabfile.org/en/1.0.1/index.html)
             Fabric is a tool that lets you run local and remote commands in the same script, thus used for 
             deployment scripts
             This script (fabric.py) is placed in the root folder where your code resides and once run it will do the following:
              1) Connect to a remote server and prepare an Ubuntu system from scratch for the deployment
                 of you Django project. It installs package dependencies you have listed.
                 ==> Python packages are installed thourhg PIP installer (http://www.pip-installer.org/) in a virtualenv
                        PIP knows what files to install through a requirements.txt file you write in the same directory
                        code root directory (where fabric.py is)
                 ==> Non Python packages are installed as usual in the Ubuntu server

              2) Zip your git project and copy it to the remote server, create a "version" folder and unpack code there.
                  Remote  folder must not exist already or it will fail.
              3) Install your application in the Apache Server

How to run:   1) First time setting up the remote Ubuntu server
                  ==> fab environment setup > deploy.log
                  ==> If it is the first time deploying this project
                         then need to create a DB, Django does not create the DB
                         mysql -u root -p
                        create database webme
  
                  ==> Dump Current Data as JSON
                         python manage.py dumpdata > data/data.webme.json
  
                  ==> Copy all the private (outside of Git)  files you have
                      added in the .gitignore but that are still needed to deploy (eg. settings files with passwords)
  
                  ==> Load JSON Dumped data into the remote DB
   
                  For details on how I use it for my project see
                  (https://github.com/adeleinr/toola/blob/master/README.txt) 
                                 
"""

from fabric.api import *
from fabric.contrib.project import rsync_project
from fabric.contrib import files, console
from fabric import utils
from fabric.operations import *

# globals
env.project_name = 'webme'

def environment():
    # Local user, same as remote for ease
    env.user = 'webme'
    #     Remote Info
    env.hosts = ['184.106.152.183']
    env.deploy_user = 'webme' 
    #     Make the version any number you want  
    env.version = 1
    env.release = env.version
    #     This is where the virtual env is created
    env.code_root = '/web/webme'
    #     This path is for activating the virtual env
    env.activate = 'source %s/bin/activate' %(env.code_root)
    #     This path is used to change permissions
    env.code_root_parent = "/web" 
    #     whole_path looks like /web/webme/releases/1/webme
    #     This is where the code really is
    env.whole_path = "%s/releases/%s/%s"%(env.code_root, env.release, env.project_name)
    #     whole_path_symlinked looks like /web/webme/releases/current/webme
    env.whole_path_symlinked = "%s/releases/current/%s"%(env.code_root, env.project_name)
    
    
def virtualenv(command):
    with cd(env.code_root):
        sudo(env.activate + '&&' + command, user=env.deploy_user)

# tasks
def test():
    "Run the test suite and bail out if it fails"
    local("cd $(code_root); python manage.py test", fail="abort")

def reset_permissions():
    sudo('chown %s -R %s'% (env.user,env.code_root_parent))
    sudo('chgrp %s -R %s'% (env.user,env.code_root_parent))

def setup():
    """
    Setup a fresh virtualenv as well as a few useful directories, then run
    a full deployment
    """
    require('hosts', provided_by=[environment])
    require('code_root')
    
    sudo('apt-get install -y python-setuptools')
    sudo('easy_install pip')
    sudo('pip install virtualenv')
    sudo('apt-get -y install git-core')
    sudo('aptitude install -y apache2')
    sudo('aptitude install -y libapache2-mod-wsgi')
    sudo('apt-get install libjpeg-dev zlib1g-dev')
    # we want rid of the defult apache config
    sudo('cd /etc/apache2/sites-available/; a2dissite default;')
    sudo('mkdir -p %s; cd %s; virtualenv .;source ./bin/activate'% (env.code_root, env.code_root))
    sudo('cd %s; mkdir releases; mkdir shared; mkdir packages;'% (env.code_root))
    reset_permissions()    
    deploy()
                                                                        
    
def deploy():
    """
    Deploy the latest version of the site to the servers, install any
    required third party modules, install the virtual host and 
    then restart the webserver
    """
    require('hosts', provided_by=[environment])
    require('whole_path', provided_by=[environment])
    require('code_root')
    # whole_path looks like /web/webme/releases/1/webme
    upload_tar_from_git(env.whole_path)
    install_requirements()
    install_nonpython_requirements()
    configure_project_specific_stuff()
    symlink_current_release()
    install_site()

    #migrate()
    restart_webserver()
    
def redeploy():
    """
    Redeploy reusing the current version, 
    this basically overwrites the code, but does not install
    any packages. Used for small changes.
    It also reuploads data from database and static files in
    media directory
    """
    upload_tar_from_git('cd %sreleases/current/%s'% (env.code_root, env.project_name))
    install_site()
    restart_webserver()

def upload_tar_from_git(path):
    require('release', provided_by=[environment])
    require('whole_path', provided_by=[environment])
    "Create an archive from the current Git main branch and upload it"
    local('git archive --format=tar main | gzip > %s.tar.gz'% (env.release))
    sudo('mkdir -p %s'% (path))
    put('%s.tar.gz'%(env.release), '/tmp', mode=0755)
    sudo('mv /tmp/%s.tar.gz %s/packages/'%(env.release, env.code_root))
    
    # After this last step the project is at:
    # /web/webme/releases/20202020202/webme
    sudo('cd %s && tar zxf ../../../packages/%s.tar.gz'% (env.whole_path, env.release))
    sudo('chown %s -R %s'% (env.user,env.whole_path))
    sudo('chgrp %s -R %s'% (env.user,env.whole_path))
    local('rm %s.tar.gz'% (env.release))
    
def install_requirements():
    "Install the required packages from the requirements file using pip"
    require('release', provided_by=[deploy, setup])
    require('whole_path', provided_by=[deploy, setup])
    sudo('cd %s; pip install -E . -r %s/requirements.txt'% (env.code_root,
                                                            env.whole_path))   
   
    reset_permissions()
                                                                          

def install_nonpython_requirements():
    "Install the required packages that cannot be installed with pip"
    require('code_root')
    require('whole_path', provided_by=[deploy, setup])
    sudo('cd %s/media_rsc/css; git clone git://github.com/joshuaclayton/blueprint-css.git'% (env.whole_path))
    sudo('chown %s -R %s'% (env.user,env.whole_path))
    sudo('chgrp %s -R %s'% (env.user,env.whole_path))
    sudo('mkdir %s/lib; cd %s/lib; curl -O http://apache.mirrors.tds.net/lucene/solr/3.1.0/apache-solr-3.1.0.tgz' % (env.whole_path, env.whole_path))
    sudo('cd %s/lib; tar xvzf apache-solr-3.1.0.tgz' % (env.whole_path))
    sudo('chown %s -R %s/lib'% (env.user,env.whole_path))
    sudo('chgrp %s -R %s/lib'% (env.user,env.whole_path))

def configure_project_specific_stuff():
    "Configure misc stuff for this project"
    require('code_root')
    require('whole_path', provided_by=[deploy, setup])
    put('/usr/local/lib/python2.6/dist-packages/django_socialregistration-0.4.2-py2.6.egg/socialregistration/views.py', '%s/src/socialregistration/socialregistration'% (env.code_root))
    sudo('chown %s -R %s'% (env.user,env.whole_path))
    sudo('chgrp %s -R %s'% (env.user,env.whole_path))

def symlink_current_release():
    "Symlink our current release"
    require('release', provided_by=[environment])
    #sudo('cd %s; rm releases/previous; mv releases/current releases/previous;' % (env.code_root))
    sudo('cd %s;ln -s %s releases/current; chown %s -R releases/current; chgrp %s -R releases/current'% (env.code_root, env.release, env.user, env.user))


def install_site():
    "Add the virtualhost file to apache"
    sudo('cd %s/releases/current/%s; cp %s /etc/apache2/sites-available/'% (env.code_root,
                                                                            env.project_name,
                                                                            env.project_name))
    sudo('cd /etc/apache2/sites-available/; a2ensite %s'% (env.project_name)) 
    

def restart_webserver():
    "Restart the web server"
    sudo('/etc/init.d/apache2 restart')
        
def migrate():
    "Update the database"
    require('project_name')
    sudo('cd %s/releases/current/;  ../../bin/python manage.py syncdb --noinput'% (env.code_root))
    

    