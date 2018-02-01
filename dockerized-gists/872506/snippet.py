from fabric.api import *

env.hosts = ['host.name.com']
env.user = 'user'
env.key_filename = '/path/to/keyfile.pem'

def local_uname():
    local('uname -a')

def remote_uname():
    run('uname -a')