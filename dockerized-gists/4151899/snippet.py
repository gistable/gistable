from fabric.api import env, local, sudo, cd
from fabric.contrib.files import append
from cuisine import user_ensure, group_ensure, group_user_ensure, file_local_read
from cuisine import select_package, package_update, package_ensure, dir_exists, run
from fabric.context_managers import prefix, settings


def vagrant():
    # change from the default user to 'vagrant'
    env.user = 'vagrant'
    # connect to the port-forwarded ssh
    env.hosts = ['127.0.0.1:2222']

    # use vagrant ssh key
    result = local('vagrant ssh-config | grep IdentityFile', capture=True)
    env.key_filename = result.split()[1]


def config_security_update(executed_now=False):
    sudo('apt-get install unattended-upgrades')
    sudo('dpkg-reconfigure -plow unattended-upgrades')


def inject_ssl_pubkey(user):
    ssl_pub = file_local_read('~/.ssh/id_dsa.pub')
    ssh_folder = '/home/{user}/.ssh/'.format(user=user)
    sudo('mkdir -p %s' % ssh_folder)
    append("/home/{user}/.ssh/authorized_keys".format(user=user), ssl_pub, use_sudo=True)
    sudo('chown -R {user}:{user} {ssh_folder}'.format(
            user=user, ssh_folder=ssh_folder))
    sudo('chmod -R 0700 %s' % ssh_folder)
    sudo('chmod 0600 %s' % "/home/{user}/.ssh/authorized_keys".format(user=user))


def uname():
    run('uname -a')


def firewall():
    cfgs = [
        "-A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT",
        "-A INPUT -p tcp -m tcp --dport 22 -j ACCEPT",
        "-A INPUT -p tcp -m tcp --dport 80 -j ACCEPT",
        "-A INPUT -p tcp -m tcp --dport 443 -j ACCEPT",
        "-A INPUT -j DROP",
    ]

    for c in cfgs:
        sudo('iptables %s' % c)

    sudo('iptables-save > /etc/iptables.up.rules')
    append('/etc/network/interfaces', "pre-up iptables-restore < /etc/iptables.up.rules",
        use_sudo=True)


def provision_user(admin_user, admin_group):
    group_ensure(admin_group)
    user_ensure(admin_user, shell='/bin/bash')
    group_user_ensure(admin_group, admin_user)
    append("/etc/sudoers", "%{group} ALL=(ALL) NOPASSWD:ALL".format(group=admin_group),
            use_sudo=True)


def prepare_rbenvs(user, rb_version='1.9.3-p194'):
    '''
    Install the ruby/rbenv under a certain user's home folder
    '''
    with settings(user=user):
        package_ensure('openssl')
        package_ensure('libopenssl-ruby1.9.1')
        package_ensure('libssl-dev')
        package_ensure('libruby1.9.1')

        with cd('~'):
            if not dir_exists('.rbenv'):
                run('git clone git://github.com/sstephenson/rbenv.git .rbenv')
                append('.bash_profile', 'export PATH="$HOME/.rbenv/bin:$PATH"')
                append('.bash_profile', 'eval "$(rbenv init -)"')
                run('git clone git://github.com/sstephenson/ruby-build.git ~/.rbenv/plugins/ruby-build')
                with prefix('source ~/.bash_profile'):
                    run('rbenv install %s' % rb_version)
                    run('rbenv rehash')
                    run('rbenv global %s' % rb_version)
                    run('gem install bundler')


def prepare_devenv():
    '''
    Pre pare the basic package for development.
    '''
    package_ensure('gcc')
    package_ensure('make')
    package_ensure('git')
    package_ensure('zlib1g-dev')
    package_ensure('libreadline-dev')

    # Admin stuff
    package_ensure('htop')
    package_ensure('vim')


def prepare_system(admin_user, admin_group='admin'):
    provision_user(admin_user, admin_group)
    inject_ssl_pubkey(admin_user)
    firewall()
    select_package('apt')
    package_update()

    prepare_devenv()
    prepare_rbenvs(admin_user)

    package_ensure('nginx')
    package_ensure('python-pip')
    sudo('pip install supervisor')
