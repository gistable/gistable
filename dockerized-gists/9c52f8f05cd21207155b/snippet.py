from fabric.api import env, sudo, local, run
 
def vagrant():
    # change from the default user to 'vagrant'
    env.user = 'vagrant'

    # Get config from vagrant ssh-config output
    result = dict(line.split() for line in local('vagrant ssh-config', capture=True).splitlines())
    # connect to the port-forwarded ssh
    env.hosts = ['%s:%s' % (result['HostName'], result['Port'])]
    # use vagrant ssh key
    env.key_filename = result['IdentityFile']
 
def uname():
    run('uname -a')