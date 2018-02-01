"""
Automated installation of ejabberd with a postgresql backend inspired by this
article: http://www.planeterlang.org/en/planet/article/How_to_install_ejabberd_2.0.0_with_PostgreSQL_support/
"""
from fabric.api import run, sudo


EJABBERD_VERSION = '2.0.5'
EJABBERD_SOURCE_HOME = '~/dev/xmpp/oss'
POSTGRES_PSQL_PASSWORD = 'user'


def install_build_tools():
    """
    Install the tools for smart packages on ubuntu
    """
    sudo('apt-get -y install build-essential checkinstall', pty=True)


def install_erlang():
    """
    Install Erlang programming language
    """
    # install erlang and ejabberd dependencies
    sudo('apt-get -y install erlang-base erlang-nox erlang-dev')


def go_to_source_home():
    """
    Create and go to the directory that stores ejabberd source.
    """
    return 'mkdir -p %(source_home)s; cd %(source_home)s; pwd;' % {
        'source_home': EJABBERD_SOURCE_HOME}


def install_ejabberd():
    """
    Install the XMPP ejabberd server from source with odbc support.
    """
    # install support libraries
    sudo('apt-get -y install libssl-dev libexpat1-dev')

    # get ejabberd source
    go_to_source_home()
    run(go_to_source_home() + \
            'wget http://www.process-one.net/downloads/downloads-action.php?file=%%2Fejabberd%%2F%(version)s%%2Fejabberd-%(version)s.tar.gz; \
            tar xzf ejabberd-%(version)s.tar.gz; \
            cd ejabberd-%(version)s/src; \
            /bin/bash configure --enable-odbc && make;' % {
        'version': EJABBERD_VERSION})

    # compile and install ejabberd
    sudo('cd %(source_home)s/ejabberd-%(version)s/src; \
        checkinstall -Dy --pkgname ejabberd --pkgversion %(version)s \
        make install' % {'source_home': EJABBERD_SOURCE_HOME,
            'version': EJABBERD_VERSION})


def install_ejabberd_modules():
    """
    Get and cd to ejabberd_modules
    """
    sudo('apt-get -y install subversion')
    run(go_to_source_home() + \
            'svn checkout http://svn.process-one.net/ejabberd-modules; \
            cd ejabberd-modules/pgsql/trunk; ./build.sh')
    sudo(go_to_source_home() + 'cd ejabberd-modules/pgsql/trunk; \
            cp ebin/* /var/lib/ejabberd/')


def install_postgresql_for_ejabberd():
    """
    Install the postgresql server, create a database for ejabberd, and
    create the necessary tables.
    """
    sudo('apt-get -y install postgresql')
    run("""sudo -u postgres psql -d template1 -c "ALTER USER postgres \
            WITH PASSWORD '%s';" """ % POSTGRES_PSQL_PASSWORD)
    run('sudo -u postgres createdb ejabberd')
    run(go_to_source_home() + \
            'wget http://svn.process-one.net/ejabberd/trunk/src/odbc/pg.sql;\
            sudo -u postgres psql ejabberd < pg.sql')


def setup_ejabberd_server():
    """
    Run a series of commands to setup a fresh ejabberd server from
    start to finish.
    """
    install_build_tools()
    install_erlang()
    install_ejabberd()
    install_ejabberd_modules()
    install_postgresql_for_ejabberd()
    

try:
    from local_fabfile import *
except ImportError:
    pass
