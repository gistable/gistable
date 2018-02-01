#!/usr/local/bin/python

# ################################################
# Matthew Ames
# Go install script
# Install command
# curl -O https://gist.githubusercontent.com/maverickames/9426462/raw/cc7e6d8d0c25be47104082b7313ce9ebc79cb436/go.py ; python go.py
# ################################################
import os
import errno

# Enviromental Settings
print "Setting up Enviroment"
version = "go1.5.2.freebsd-amd64.tar.gz"
url = "https://storage.googleapis.com/golang/" + version
devel_dir = "/usr/home/lsadmin"
goPath = devel_dir + '/go_devel'

print 'Downloading: {0}'.format(version)
print 'url location: {0}'.format(url)
print 'Devel folder: {0}'.format(goPath)

def create_folder(path):
    print path
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

# Download go
print "Downloading GO language";
os.system('curl -O {0}'.format(url))

# Install GO
print "Installing GO";
os.system('tar -C /usr/local -xzf {0}'.format(version))

# Setup GO folders
print "Setting up GO folders";
create_folder(devel_dir + "/go_devel/")
create_folder(devel_dir + "/go_devel/src")
create_folder(devel_dir + "/go_devel/pkg")
create_folder(devel_dir + "/go_devel/bin")

# Setup users devel github folders
print "Setup users devel github folders";
create_folder(devel_dir + "/go_devel/src/github.com/")
create_folder(devel_dir + "/go_devel/src/github.com/maverickames")

os.system('echo setenv PATH $PATH:/usr/local/go/bin >> $HOME/.cshrc')
os.system('echo setenv GOPATH {0} >> $HOME/.cshrc'.format(goPath))
os.system('source $HOME/.cshrc')

print ('Install should be complete')
print ('Try run: go')
