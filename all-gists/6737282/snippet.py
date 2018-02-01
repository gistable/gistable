"""
Installs your SSH key on other hosts. A fabfile for lazy people.
"""

from fabric.api import task, run, put, env, cd

# Use sh instead of bash.
env.shell = '/bin/sh -l -c'

@task
def add_ssh_key(identity='~/.ssh/id_rsa.pub'):
    # Copy the key over.
    REMOTE_PATH = '~/id.pub'
    put(identity, REMOTE_PATH)

    with cd('~'):
        # Make sure the SSH directory is created.
        run('mkdir -p .ssh')
        # And append to the authrized keys.
        run('cat %(REMOTE_PATH)s >> ~/.ssh/authorized_keys' % locals())
        # Be thourough and leave no trace of this interaction!
        run('rm %(REMOTE_PATH)s' % locals())

