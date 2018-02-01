#!/usr/bin/env fab
# vim:ts=4:sw=4:tw=120:et:sm:foldmethod=indent

import os
import time

from fabric.api import *
from fabric.contrib import files

# Global Settings
# ===============
env.project_name = "foobar"
env.user = "username"
#env.email_pass = @.fabricrc
#env.db_passwd = @.fabricrc
#env.db_root_passwd = @.fabricrc
env.db_name = env.project_name
env.db_username = env.project_name
env.hosts = ['server:22222']
env.path = "/var/www/%(project_name)s" % env
env.key_filename = os.path.realpath(os.path.expanduser("~/.ssh/username.key"))
env.localdir = os.path.realpath(os.path.join(os.path.dirname(env.real_fabfile), ".."))
env.disable_known_hosts = True  # ignore key changes on remote hosts. Useful for cloud environments.


# Utilities
def _install_packages(debpacks):
    with settings(warn_only=True):
        sudo("DEBIAN_FRONTEND=noninteractive aptitude -q -y install %s" % (' '.join(debpacks),))


def _full_upgrade():
    with settings(warn_only=True):
        sudo("DEBIAN_FRONTEND=noninteractive aptitude -q -y update")
        sudo("DEBIAN_FRONTEND=noninteractive aptitude -q -y full-upgrade")


def _restart_service(service):
    sudo("service %s stop" % (service,))
    time.sleep(5)
    sudo("service %s start" % (service,))


# Setup
def _setup_base_packages():
    files.uncomment("/etc/apt/sources.list", "deb .*universe", use_sudo=True)

    sudo("wget -q -ct0 'http://packages.ourserver.com/ubuntu/dists/lucid/ourrepo/ourrepo.list' -O /etc/apt/sources.list.d/ourrepo.list")
    sudo("$(apt-key list | grep 'Our Key' > /dev/null) || apt-key adv --keyserver keyserver.ubuntu.com --recv-keys DEADBEEF")

    _full_upgrade()


def _setup_users():
    sudo("usermod -G %(user)s www-data" % env)


def _setup_directories():
    sudo("mkdir -p %(path)s" % env)
    sudo("chown %(user)s:%(user)s %(path)s" % env)

    directories = (
        ("backups", "0700"),
        ("certs", "0750"),
        ("logs", "2770"),
        ("media", "0750"),
        ("media/resources", "0750"),
        ("media/resources/public", "2770"),
        ("media/resources/private", "2770"),
        ("media/system", "0750"),
        ("python", "0750"),
    )

    for directory, permission in directories:
        path = os.path.join("%(path)s" % env, directory)
        run("mkdir -p %r" % path)
        run("chmod %s %s" % (permission, path))


def _setup_basic_security():
    _install_packages([
        'ufw',
        'fail2ban',
    ])

    files.sed("/etc/ufw/ufw.conf", "ENABLED=no", "ENABLED=yes", use_sudo=True)
    sudo("/usr/sbin/ufw --force reset")
    sudo("/usr/sbin/ufw default deny")
    sudo("/usr/sbin/ufw allow SSHPORT")
    sudo("/usr/sbin/ufw allow 80")
    sudo("/usr/sbin/ufw allow 443")
    sudo("/usr/sbin/ufw --force enable")
    sudo("rm -f /lib/ufw/user*.rules.*")


def _setup_database():
    if files.exists("/var/lib/mysql/%(project_name)s" % env, use_sudo=True):
        return

    _install_packages([
        'mysql-common',
        'mysql-server-5.1',
    ])

    with hide("running"):
        run("/usr/bin/mysqladmin -f -u root create %(db_name)s" % env)
        run("echo \"GRANT ALL ON %(db_name)s.* TO %(db_username)s@127.0.0.1 IDENTIFIED BY '%(db_passwd)s';\" | /usr/bin/mysql -u root" % env)
        run("echo \"GRANT ALL ON %(db_name)s.* TO %(db_username)s@localhost IDENTIFIED BY '%(db_passwd)s';\" | /usr/bin/mysql -u root" % env)
        run("/usr/bin/mysqladmin -u root password '%(db_root_passwd)s'" % env)


def _setup_python_environment():
    _install_packages([
        'language-pack-pt-base',
        'python-pip',
        'python-virtualenv',
        'python-mysqldb',
        'python-yaml',
        'git-core',
        'gcj-4.4-jre-headless',
    ])

    sudo("pip install -q -U pip")
    sudo("pip install -q -U distribute")
    sudo("pip install -q -U virtualenv")

    if not files.exists("%(path)s/python/bin/activate" % env):
        run("virtualenv --distribute %(path)s/python" % env)

    run("%(path)s/python/bin/pip install -q django==1.2.3" % env)
    run("%(path)s/python/bin/pip install -q South" % env)
    run("%(path)s/python/bin/pip install -q docutils" % env)

    # Git Clone
    put("%(localdir)s/deploy/keys/SSHKEY.key" % env, "~/.ssh/id_dsa" % env)
    put("%(localdir)s/deploy/keys/SSHKEY.key.pub" % env, "~/.ssh/id_dsa.pub" % env)
    run("chmod 0600 ~/.ssh/id_dsa*")
    run("echo 'StrictHostKeyChecking no' > ~/.ssh/config")
    deploy(restart=False)


def _setup_apache():
    _install_packages([
        'libapache2-mod-wsgi',
        'libapache2-mod-php5',
    ])

    files.upload_template("%(localdir)s/deploy/apache-main.conf" % env,
            "/etc/apache2/apache2.conf", use_sudo=True)

    files.upload_template("%(localdir)s/deploy/apache-site.conf" % env,
            "/etc/apache2/sites-available/%(project_name)s" % env, use_sudo=True)

    files.upload_template("%(localdir)s/deploy/standby.conf" % env,
            "/etc/apache2/sites-available/standby", use_sudo=True)

    local("cd %(localdir)s/deploy/503 && tar cjf ../503.tar.bz2 *" % env)
    files.put("%(localdir)s/deploy/503.tar.bz2" % env, "/tmp")
    sudo("tar xf /tmp/503.tar.bz2 -C /var/www && rm /tmp/503.tar.bz2")
    local("rm -f %(localdir)s/deploy/503.tar.bz2" % env)

    sudo("/usr/sbin/a2dismod "
         "cgid auth_basic authn_file authz_default authz_user "
         "authz_groupfile autoindex negotiation setenvif deflate")

    sudo("/usr/sbin/a2dissite default default-ssl standby")
    sudo("/usr/sbin/a2ensite %(project_name)s" % env)

    sudo("rm -f /var/www/index.html")

    _restart_service("apache2")


def _setup_nginx():
    _install_packages([
        'nginx',
    ])

    with hide("running"):
        local("(cd %(localdir)s/deploy/certs && gpg --no-use-agent --batch --passphrase '%(new_pass)s' -o all.certs.tar -d all.certs.tar.gpg)" % env)

    local("(cd %(localdir)s/deploy/certs && tar xf all.certs.tar)" % env)
    local("(cd %(localdir)s/deploy/certs/all.cert && cat gd_bundle.crt >> all.crt)" % env)
    local("(cd %(localdir)s/deploy/certs/all.cert && cp all.key all.key.orig)" % env)

    with hide("running"):
        local("(cd %(localdir)s/deploy/certs/all.cert && openssl rsa -in all.key.orig -out all.key -passin 'pass:%(new_pass)s' )" % env)

    files.upload_template("%(localdir)s/deploy/certs/all.cert/all.crt" % env,
            "%(path)s/certs/" % env, use_sudo=True)
    files.upload_template("%(localdir)s/deploy/certs/all.cert/all.key" % env,
            "%(path)s/certs/" % env, use_sudo=True)

    sudo("chmod 0400 %(path)s/certs/*" % env)

    local("(cd %(localdir)s/deploy/certs && rm -f *.tar sf_bundle.crt *.pem)" % env)
    local("(cd %(localdir)s/deploy/certs && rm -r all.cert)" % env)

    files.upload_template("%(localdir)s/deploy/nginx-site.conf" % env,
            "/etc/nginx/sites-available/%(project_name)s" % env, use_sudo=True)

    files.upload_template("%(localdir)s/deploy/nginx-main.conf" % env,
            "/etc/nginx.conf", use_sudo=True)

    sudo("rm -f /etc/nginx/conf.d/*")
    sudo("rm -f /etc/nginx/sites-enabled/*")
    sudo("ln -sf /etc/nginx/sites-available/%(project_name)s "
         "/etc/nginx/sites-enabled/%(project_name)s" % env)

    _restart_service("nginx")


def setup():
    _setup_base_packages()
    _setup_users()
    _setup_directories()
    _setup_basic_security()
    _setup_database()
    _setup_python_environment()
    _setup_apache()
    _setup_nginx()


# Deploy
def _deploy_backup_db():
    sudo("mysqldump -u%(db_username)s -p%(db_passwd)s %(db_name)s > %(path)s/backups/mysql-$(date --iso).sql" % env)


def _deploy_pull():
    if not files.exists("%(path)s/%(project_name)s" % env):
        run("ssh-agent sh -c 'ssh-add ~/.ssh/id_dsa && "
            "cd %(path)s && git clone GIT_REPO %(project_name)s'" % env)
    else:
        run("ssh-agent sh -c 'ssh-add ~/.ssh/id_dsa && cd %(path)s/%(project_name)s && git pull'" % env)


def _deploy_syncdb():
    cmd = "%(path)s/python/bin/python %(path)s/%(project_name)s/" % env
    run(cmd + "manage.py syncdb --settings=%(project_name)s.settings.production --noinput" % env)  # syncdb
    # FIXME: try to improve (and remove this setting using umask(?))
    run("chmod g+w %(path)s/logs/*.log" % env)


def _deploy_migrate():
    cmd = "%(path)s/python/bin/python %(path)s/%(project_name)s/" % env
    run(cmd + "manage.py migrate --settings=%(project_name)s.settings.production" % env)  # migrate


def _deploy_create_admin():
    cmd = "%(path)s/python/bin/python %(path)s/%(project_name)s/" % env
    with hide("running"):
        run(cmd + "manage.py createadmin --settings=%(project_name)s.settings.production "
            "--username '%(project_name)s' "
            "--email %(project_name)s@example.com "
            "--password %(new_pass)s" % env)


def _deploy_minify():
    run("%(path)s/%(project_name)s/deploy/minify.sh %(path)s/%(project_name)s/media %(path)s/media/system" % env)
    run("ln -sf %(path)s/python/lib/python*/site-packages/django/contrib/admin/media "
         "%(path)s/media/admin" % env)


def deploy(restart=True):
    _deploy_backup_db()  # backup
    _deploy_pull()  # pull
    _deploy_syncdb()  # syncdb
    _deploy_migrate()  # migrate
    _deploy_minify()  # minify

    if restart:
        _restart_service("apache2")
        _restart_service("nginx")


# Miscelaneous
def maintenance_on():
    sudo("/usr/sbin/a2dissite %(project_name)s" % env)
    sudo("/usr/sbin/a2ensite standby")
    _restart_service("apache2")


def maintenance_off():
    sudo("/usr/sbin/a2dissite standby")
    sudo("/usr/sbin/a2ensite %(project_name)s" % env)
    _restart_service("apache2")


def restart_nginx():
    _restart_service("nginx")


def restart_apache():
    _restart_service("apache2")
