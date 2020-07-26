#!/usr/bin/env python
"""
fabfile.py

Copyright (c) 2011 Giovanni Collazo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import os
import time
import boto
from fabric.api import *

PROJECT_NAME = os.path.realpath(os.path.dirname(__file__)).split('/')[-1]
APPS_DIR = "/var/webapps"
STATIC_DIR = "static"
DOMAINS = "example.com www.example.com"
DB_PWD = "password"
VIRTUALENV_DIR = "~/.virtualenvs"
GIT_USERNAME = "Server"
ADMIN_EMAIL = "webmain@localhost"
GITHUB_DEPLOY_KEY = "/Users/username/.ssh/github"
GITHUB_REPO = "git@github.com:username/repository.git"

ec2_key = 'ec2key'
ec2_secret = 'ec2secret'
ec2_amis = ['ami-ccf405a5']
ec2_keypair = 'ec2keypairname'
ec2_secgroups = ['ec2-security-group-name']
ec2_instancetype = 't1.micro'

env.user = 'ubuntu'
env.key_filename = '/Users/username/.ssh/ec2keypairname.pem'
env.hosts = ['']

def first_deploy():
  """
  Setup app for the first time
  """
  with cd(APPS_DIR):
    run("git clone %s" % GITHUB_REPO)
    restart_apache()

def restart_apache():
  """
  Restarts apache
  """
  sudo("/etc/init.d/apache2 restart")

def restart_nginx():
  """
  Restarts nginx
  """
  sudo("/etc/init.d/nginx restart")

def bootstrap_server():
  """
  Install packages and setup server
  """
  
  # Install packages
  sudo("apt-get update -qq")
  sudo("apt-get upgrade -qq")
  run("echo 'mysql-server mysql-server/root_password select %s' | sudo debconf-set-selections && echo 'mysql-server mysql-server/root_password_again select %s' | sudo debconf-set-selections && sudo apt-get install -qq mysql-server" % (DB_PWD, DB_PWD))
  sudo("apt-get install -qq mysql-client")
  sudo("apt-get install -qq apache2 libapache2-mod-wsgi")
  sudo("apt-get install -qq nginx")
  sudo("apt-get install -qq python-setuptools python-dev build-essential python-pip")
  sudo("apt-get install -qq nginx")
  sudo("apt-get -qq install git")
  sudo("pip install django")
  sudo("pip install fabric")
  sudo("pip install virtualenv")
  sudo("pip install virtualenvwrapper")
  
  # Apache setup: serv application with mod_wsgi
  # /etc/apache2/sites-available/default
  run("""echo '<VirtualHost *:8080>
  	ServerAdmin %s
  	WSGIScriptAlias / %s
  	<Directory />
  		Order allow,deny
  		Allow from all
  	</Directory>
  	ErrorLog ${APACHE_LOG_DIR}/error.log
  	LogLevel warn
  	CustomLog ${APACHE_LOG_DIR}/access.log combined
  </VirtualHost>' > ~/default""" % (ADMIN_EMAIL, os.path.join(APPS_DIR, PROJECT_NAME, "django.wsgi")))
  sudo("rm -rf /etc/apache2/sites-available/default")
  sudo("mv ~/default /etc/apache2/sites-available/default")
  sudo("chown root:root /etc/apache2/sites-available/default")
  
  # /etc/apache2/ports.conf
  run("""echo "NameVirtualHost *:8080
  Listen 8080
  <IfModule mod_ssl.c>
      Listen 443
  </IfModule>
  <IfModule mod_gnutls.c>
      Listen 443
  </IfModule>" > ~/ports.conf""")
  sudo("rm -rf /etc/apache2/ports.conf")
  sudo("mv ~/ports.conf /etc/apache2/ports.conf")
  sudo("chown root:root /etc/apache2/ports.conf")
  
  restart_apache()
  
  # Nginx setup: serv media files and proxy all other request
  # /etc/nginx/nginx.conf
  run("""echo "user www-data;
  worker_processes  2;
  error_log  /var/log/nginx/error.log;
  pid        /var/run/nginx.pid;
  events {
      worker_connections  1024;
  }
  http {
      include       /etc/nginx/mime.types;
      default_type  application/octet-stream;
      access_log  /var/log/nginx/access.log;
      sendfile        on;
      tcp_nopush     on;
      keepalive_timeout  65;
      tcp_nodelay        on;
      gzip  on;
      include /etc/nginx/conf.d/*.conf;
      include /etc/nginx/sites-enabled/*;
  }" > ~/nginx.conf""")
  sudo("rm -rf /etc/nginx/nginx.conf")
  sudo("mv ~/nginx.conf /etc/nginx/nginx.conf")
  sudo("chown root:root /etc/nginx/nginx.conf")
  
  # /etc/nginx/sites-enabled/default
  run("""echo "server {
  	listen   80; ## listen for ipv4
  	listen   [::]:80 default ipv6only=on; ## listen for ipv6
  	server_name %s;
  	access_log  /var/log/nginx/localhost.access.log;
  	error_log /var/log/nginx/localhost.error.log;
  	location / {
      proxy_pass http://127.0.0.1:8080;
      include /etc/nginx/proxy.conf;
    }
    location /%s/ {
      root   %s;
    }
  }" > ~/default""" % (DOMAINS, STATIC_DIR, os.path.join(APPS_DIR, PROJECT_NAME)))
  sudo("rm -rf /etc/nginx/sites-available/default")
  sudo("mv ~/default /etc/nginx/sites-available/default")
  sudo("chown root:root /etc/nginx/sites-available/default")
  
  # /etc/nginx/proxy.conf
  run("""echo 'proxy_redirect              off;
  proxy_set_header            Host $host;
  proxy_set_header            X-Real-IP $remote_addr;
  proxy_set_header            X-Forwarded-For $proxy_add_x_forwarded_for;
  client_max_body_size        10m;
  client_body_buffer_size     128k;
  proxy_connect_timeout       90;
  proxy_send_timeout          90;
  proxy_read_timeout          90;
  proxy_buffer_size           4k;
  proxy_buffers               4 32k;
  proxy_busy_buffers_size     64k;
  proxy_temp_file_write_size  64k;
  ' > ~/proxy.conf""")
  sudo("rm -rf /etc/nginx/proxy.conf")
  sudo("mv ~/proxy.conf /etc/nginx/proxy.conf")
  sudo("chown root:root /etc/nginx/proxy.conf")
  
  restart_nginx()
  
  # Make virtualenvwrapper work
  sudo("mkdir %s" % VIRTUALENV_DIR)
  sudo("chown -R ubuntu:ubuntu %s" % VIRTUALENV_DIR)
  run('echo "export WORKON_HOME=%s" >> ~/.profile' % VIRTUALENV_DIR)
  run('echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.profile')
  run("source ~/.profile")
  
  # Make a webapps alias
  run("""echo "alias webapps='cd %s'" >> ~/.profile""" % APPS_DIR)
  
  # Create WebApps Folder
  sudo("mkdir %s" % APPS_DIR)
  sudo("chown -R ubuntu:ubuntu %s" % APPS_DIR)
  
  # Setup git
  run("git config --global user.name %s" % GIT_USERNAME)
  run("git config --global user.email %s" % ADMIN_EMAIL)
  put(GITHUB_DEPLOY_KEY, "~/.ssh/%s" % GITHUB_DEPLOY_KEY.split('/')[-1])
  run("chmod 600 ~/.ssh/%s" % GITHUB_DEPLOY_KEY.split('/')[-1])
  run("""echo 'IdentityFile ~/.ssh/%s' >> ~/.ssh/config""" % GITHUB_DEPLOY_KEY.split('/')[-1])
  run('ssh-keyscan github.com > ~/.ssh/known_hosts')

def create_server():
  """
  Creates an fresh EC2 instance
  """
  conn = boto.connect_ec2(ec2_key, ec2_secret)
  image = conn.get_all_images(ec2_amis)

  reservation = image[0].run(1, 1, ec2_keypair, ec2_secgroups,
    instance_type=ec2_instancetype)

  instance = reservation.instances[0]

  while instance.state == u'pending':
    print "Instance state: %s" % instance.state
    time.sleep(10)
    instance.update()

  print "Instance state: %s" % instance.state
  local("echo %s | pbcopy" % instance.public_dns_name)
  print "Public dns: %s" % instance.public_dns_name
  
  print "*** Edit env.hosts to include hostname, then run 'setup_instance' ***"