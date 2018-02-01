# http://unfoldthat.com/2012/06/02/quick-deploy-chef-solo-fabric.html

from fabric.api import settings, run, sudo, reboot, put, cd, env

AWS_ACCESS_KEY = '...'
AWS_SECRET_KEY = '...'

AWS_KEYPAIR_NAME = '...'

AWS_SECURITY_GROUPS = ['default']

#AMI_IMAGE_ID = 'ami-c670d7af'
AMI_IMAGE_ID = 'ami-f60bad9f'

env.connection_attempts = 4

def _ec2_connection():
    from boto.ec2.connection import EC2Connection

    return EC2Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY)


def _add_line_if_not_present(filename, line, run_f=run):
    run_f("grep -q -e '%s' %s || echo '%s' >> %s" % (line, filename, line, filename))




def update_server():
    with cd('~/deploy/'):
        run('git pull')

        sudo('chef-solo -c solo.rb -j dna.json')

        

def set_up_new_server(name):
    instance = run_new_server(name)

    with settings(host_string='ubuntu@%s' % instance.public_dns_name):
        prepare_new_server(name)
        checkout_deploy()
        update_server()



def run_new_server(name):
    name = 'uploadcare-%s' % name
    conn = _ec2_connection()

    print 'Running a new instance...'

    rs = conn.run_instances(AMI_IMAGE_ID,
                            key_name=AWS_KEYPAIR_NAME,
                            security_groups=AWS_SECURITY_GROUPS,
                            instance_type='m1.medium',
                            placement='us-east-1b')
#                            disable_api_termination=True)

    instance = rs.instances[0]

    print 'Setting name to:', name
    instance.add_tag('Name', name)

    print 'Waiting for instance...'
    while instance.update() == 'pending':
        pass

    print 'Got it! Instance state is:   ', instance.state
    print 'Instance public DNS:', instance.public_dns_name

    return instance

def prepare_new_server(name):
    _add_line_if_not_present('/etc/hosts', '127.0.0.1 %s' % name, sudo)

    sudo('hostname %s' % name)
    sudo('apt-get update')
    sudo('apt-get upgrade -y')
    sudo('apt-get update')
    sudo('apt-get install -y git ruby1.9.1 ruby1.9.1-dev build-essential')
    sudo('gem install chef --no-ri --no-rdoc')

    print 'Rebooting to apply stuff...'
    reboot()


def checkout_deploy():
    run('mkdir ~/.ssh/ || true')
    run('chmod 700 ~/.ssh/')
    put('files/deploy_key', '~/.ssh/id_rsa')
    put('files/deploy_key.pub', '~/.ssh/id_rsa.pub')
    run('chmod 600 ~/.ssh/id_*')

    run('echo  >> ~/.ssh/known_hosts')

    _add_line_if_not_present('~/.ssh/known_hosts', "github.com,207.97.227.239 ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAq2A7hRGmdnm9tUDbO9IDSwBK6TbQa+PXYPCPy6rbTrTtw7PHkccKrpp0yVhp5HdEIcKr6pLlVDBfOLX9QUsyCOV0wzfjIJNlGEYsdlLJizHhbn2mUjvSAHQqZETYP81eFzLQNnPHt4EVVUh7VfDESU84KezmD5QlWpXLmvU31/yMf+Se8xhHTvKSCZIFImWwoG6mbUoWf9nzpIoaSjB+weqqUUmpaaasXVal72J+UX2B+2RPW3RcT0eOzQgqlJL3RKrTJvdsjE3JEAvGq3lGHSZXy28G3skua2SmVi/w4yCE6gbODqnTWlg7+wC604ydGXA8VJiS5ap43JXiUFFAaQ==")

    run('git clone git@github.com:uploadcare/deploy.git')


