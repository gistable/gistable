# -*- coding: utf-8 -*-
"""MyCompany Fabric script.

* Deploy code
* Set up a local development environment

There are two ways to deploy the myrepo code:

1.  :func:`deploy` will do a full virtualenv installation/update and expand a
    tarball of the specified git revision (defaults to HEAD) to a timestamped
    directory and restart Apache.
2.  :func:`rsync` will copy any local files that have changed to the server and
    restart Apache. Intended for quick checks without requiring a git commit;
    this should never be used on a production machine.

----------------------------------------------------------------

**Usage Examples**::

    $ fab somecommand

.. cmdoption:: -l, --list

    List all available commands.

.. cmdoption:: -d, --display

    Verbose help for a given command.

.. cmdoption:: -R, --roles

    Run a command only on specific groups. For example, to copy your ssh public
    key to all staging web servers::

        fab -R web env_staging do_sshkey

.. cmdoption:: -- command

    Run a custom command on all hosts. For example, to get the kernel version for all
    staging systems::

        fab -R all env_staging -- uname -a

.. cmdoption:: -h, --help

    See all Fabric options.

----------------------------------------------------------------

**Prefixes:**

* ``env_*`` functions should set all necessary options to make changes to
  non-localhost systems.
* ``do_*`` functions should be generic enough to run on any host, real or
  virtual, development or production.
* ``vbox_*`` functions should be specific to setting and configuring up
  VirtualBox environments.

----------------------------------------------------------------

"""
# TODO: add South integration
# TODO: integrate install_flex_app.py
# TODO: does legacyperl need its own deploy() ?
# TODO: run the test suite before a deployment

# NOTE: multi-host deployments is completely untested.
# FIXME: Issue #21 for convenient multi-host deployments
# http://article.gmane.org/gmane.comp.python.fab.user/1014
# FIXME: Issue #38 for deployment through the gateway server
# http://code.fabfile.org/issues/show/38

from __future__ import with_statement # python 2.5 compat

import datetime
import distutils.version
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import textwrap
import time
import urllib
import urlparse
import BaseHTTPServer
import SimpleHTTPServer

import fabric
import fabric.state
import fabric.api as _fab

##### Default settings
###############################################################################
DEFAULT_VALUES = {
    'GUEST': 'mydevenv',
    'PATH': '/var/www/mydomain.com',
    'MEDIA_ROOT': '/var/www/mydomain.com/media_root',
    'DOMAIN': 'mycode-local.mydomain.com',
    'URI': 'http://mycode-local.mydomain.com:8080',
    'SSH_PORT': '2222',
    'HTTP_PORT': '8080',
    'DVCS': 'git',
    'VERSION': 'HEAD',
    'VBOX_MIN_VER': distutils.version.LooseVersion('3.1'),
    'GIT_MIN_VER': distutils.version.LooseVersion('1.6.3.3'),
    'HEADLESS': False,
    'TMPL': os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../../fab_templates')),
}
"""These values may be overridden by creating a :file:`~/.fabricrc` containing
``key = value`` pairs.

You can override the default ports VirtualBox uses, the default guest name, use
Mercurial instead of git, default to headless operation, etc. See the source
for the full list.

"""

# This file is annoyingly processed *after* env is populated by command-line
# or ~/.fabricrc options, so we need those options to take precedence.
for k,v in DEFAULT_VALUES.items():
    if not k in _fab.env.keys():
        _fab.env[k] = v

# Small hack to facilitate Mercurial
if _fab.env.get('DVCS') == 'hg' and _fab.env.get('VERSION') == 'HEAD':
    _fab.env['VERSION'] = 'tip'

##### Environments
###############################################################################
# All operations default to localhost
LOCALHOST = ['mylogin@localhost:%(SSH_PORT)s' % _fab.env]
ROLEDEFS = {
    'web': LOCALHOST,
    'db': LOCALHOST,
    'memcached': LOCALHOST,
}
"""Fabric runs commands on lists of hosts, called :data:`ROLEDEFS`. All
operations are performed on localhost by default. To make changes to
:term:`staging` or :term:`production`, you must set the proper :data:`ROLEDEFS`
by calling :func:`env_staging` or :func:`env_production`.

:data:`ROLEDEFS` describe groups of machines. Each task is defined to run for
certain groups. For example, :func:`deploy` might put the code onto the web
servers, restart the webservers, run migrations on the database servers, and
prime the caches on the memcached servers; whereas :func:`restart` will only
run on the webservers.

"""

_fab.env.roledefs.update(ROLEDEFS)
_fab.env.roledefs['all'] = ROLEDEFS.values()[0]
# TODO: Fabric 1.0 supports callables for roledefs. Once it is released you can
# replace all the manual ['all'] settings with the following one line:
# _fab.env.roledefs['all'] = lambda: _fab.env.roledefs.values()[0]

def env_staging():
    """Make changes on the staging server(s)

    This is required to affect hosts other than localhost.

    """
    HOST = ['tools@mycompany-stage.mydomain.com']

    _fab.env.roledefs.update({
        'web': HOST,
        'db': HOST,
        'memcached': HOST,
    })
    _fab.env.roledefs['all'] = HOST

def env_production():
    """Make changes on the production! servers

    This is required to affect hosts other than localhost.

    """
    if (not socket.gethostname() in ('synic',)
        and not fabric.contrib.console.confirm(textwrap.dedent("""\
                You are trying to make changes to the live servers! The only
                person that should do this is Adam. You don't look like Adam.
                Are you absolute sure what you're trying to do won't get you
                fired?"""), default=False)):

        _fab.abort('Dodged a bullet there.')

    _fab.env.roledefs.update({
        'web': ['10.1.1.15', '10.1.1.16', '10.1.1.17', '10.1.1.18'],
        'db': ['10.1.1.12', '10.1.1.13'],
        'memcached': ['10.1.1.15', '10.1.1.16', '10.1.1.17', '10.1.1.18'],
    })

    all = _fab.env.roledefs['web']
    all.extend(_fab.env.roledefs['db'])
    all.extend(_fab.env.roledefs['memcached'])
    _fab.env.roledefs['all'] = all

##### Helpers Functions
###############################################################################
def _local(*args, **kwargs):
    """A wrapper around fabric.local() that takes a list. It will take care of
    the shell quoting for you. This makes interspersing variables a bit easier.

    E.g.: instead of::

        local('echo "Hello, this has spaces in it.")

    Use::
        
        _local(['echo', 'This has spaces in it.'])

    """
    return _fab.local(subprocess.list2cmdline(*args), **kwargs)

def _write(string, desc='stdout'):
    """Write formatting strings suitable for the terminal."""
    out = getattr(sys, desc, 'stdout')
    for line in textwrap.dedent(string).split('\n'):
        out.write(textwrap.fill(line, width=79) + '\n')
    out.flush()

def _str2bool(string):
    """Returns a boolean value based on a string input."""
    if not isinstance(string, str):
        return string

    if string.lower() in ['true', 'y', 'yes', '1', 'yeah']:
        return True

    return False

def _get_vcs_archive_cmd():
    """A hack to allow for either git or Mercurial usage."""
    if _fab.env.get('DVCS') == 'git':
        return 'cd ./$(git rev-parse --show-cdup) && git archive '\
            '--prefix="%(basename)s/" --output %(fullpath)s %(version)s'
    elif _fab.env.get('DVCS') == 'hg':
        return 'hg archive -t tar -r %(version)s %(fullpath)s'

@_fab.roles('all')
def do_metadeb():
    """Install required software on a Ubuntu system

    See :file:`myrepo/fab_templates/debian-control.tmpl` for a complete list of
    all required software packages.

    You probably want to reboot after this to start any new services.

    """
    _fab.put('%(TMPL)s/debian-pkgs.txt' % _fab.env, '/tmp/debian-pkgs.txt')
    _fab.sudo('aptitude -y install $(cat /tmp/debian-pkgs.txt)')

@_fab.roles('all')
def do_sshkey():
    """Install your SSH public key

    This is a wrapper around :command:`ssh-copy-id` which runs on all currently
    defined Fabric hosts.
    
    """
    with _fab.settings(warn_only=True):
        for host in _fab.env.all_hosts:
            o = urlparse.urlparse('svn+ssh://%s' % host)
            _fab.local("ssh-copy-id '-p %s %s@%s'" % (
                o.port, o.username, o.hostname))

@_fab.roles('all')
def do_vpn(action='up'):
    """Creates an SSH VPN

    Usage::

        # Start a new VPN connection
        do_vpn

        # Stop an old VPN connection
        do_vpn:action=down

    This automates some of the bookkeeping of establishing a VPN via SSH.
    This is useful to allow a direct connection to a private network (such as
    the production machines) from your local machine.

    """
    # Stolen from EnigmaCurry <http://wiki.enigmacurry.com/OpenSSH>
    # NOTE: This is TCP-over-TCP; both inefficient and high-latency.

    for host in _fab.env.all_hosts:
        conn = Connection(host)
        getattr(conn, action)()

@_fab.roles('web')
def do_tests():
    """Run the test suite and bail out if it fails"""
    _fab.local("./manage.py test mycode", fail="abort")

@_fab.roles('web')
def do_pyc():
    """Remove pyc files from the project dir"""
    _fab.local("find %s -name '*.pyc' -depth -exec rm {} \;" % (
        os.path.dirname(__file__),))

@_fab.roles('db')
def do_postgres():
    """Create a Postgres database and database user
    
    Since we're on Postgres now, we might as well add GIS too since we almost
    get it for free. Bonus points for thinking up a way to actually use
    geo-spatial functionality somewhere on the site. :)

    """
    DB_USER = 'devdb'
    DB_NAME = 'devdb'

    # FIXME: Ubuntu 8.04 LTS is too out of date so we cannot get GIS for
    # *free*. It requires installing a few packages from source. Thus, this is
    # commented out for now.
    # PGIS_SQL = _fab.run('`pg_config --sharedir`/contrib', user='postgres')

    # Ubuntu doesn't include the datum shifting files for some reason
    # with _fab.cd('/tmp'):
        # _fab.run('wget http://download.osgeo.org/proj/proj-datumgrid-1.4.tar.gz')
        # _fab.run('mkdir nad')

        # with _fab.cd('nad'):
            # _fab.run('tar xzf ../proj-datumgrid-1.4.tar.gz')
            # _fab.run('nad2bin null < null.lla')
            # _fab.sudo('cp null /usr/share/proj')

    # Ubuntu doesn't run this post-install for some reason
    # _fab.sudo('pg_createcluster --start 8.3 main')

    # Ubuntu puts the spatial ref sql files in the wrong place for some reason
    # _fab.sudo('ln -sfn /usr/share/postgresql-8.3-postgis/{lwpostgis,spatial_ref_sys}.sql /usr/share/postgresql/8.3')

    # Create the GIS template
    # _fab.sudo('createdb -E UTF8 template_postgis', user='postgres')
    # _fab.sudo('createlang -d template_postgis plpgsql', user='postgres')
    # _fab.sudo('psql -d postgres -c "UPDATE pg_database SET datistemplate=\'true\' WHERE datname=\'template_postgis\';"', user='postgres')
    # _fab.sudo('psql -d template_postgis -f $POSTGIS_SQL_PATH/postgis.sql', user='postgres')
    # _fab.sudo('psql -d template_postgis -f $POSTGIS_SQL_PATH/spatial_ref_sys.sql', user='postgres')
    # _fab.sudo('psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;"', user='postgres')
    # _fab.sudo('psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"', user='postgres')

    # Create the database
    with _fab.settings(warn_only=True):
        _fab.sudo('createuser --no-superuser --no-createrole '\
                '--createdb %s' % DB_USER, user='postgres')
        # _fab.sudo('createdb -T template_postgis %s' % DB_NAME, user='postgres')
        _fab.sudo('createdb -O %s %s' % (DB_USER, DB_NAME), user='postgres')

@_fab.roles('web')
def do_apache_vhost():
    """Add a vhost entry to ``sites-available`` and enable it"""

    path = '/etc/apache2/sites-available'

    if not fabric.contrib.files.exists(path):
        _fab.abort(textwrap.dedent("""\
            Could not determine the location of your Apache vhost config
            file."""))

    fabric.contrib.files.upload_template(
            '%(TMPL)s/httpd-vhosts.conf.tmpl' % _fab.env,
            '%s/mydomain.com' % path,
            context=_fab.env,
            use_sudo=True)

    _fab.sudo('mkdir -p /var/www/mydomain.com/logs')
    _fab.sudo('a2ensite mydomain.com')

    restart(hard=True)

@_fab.roles('web')
def do_pythonlibs():
    """Install required Python libraries

    These are not often kept up to date in apt.

    """
    with _fab.hide('stdout', 'stderr'):
        _fab.sudo('easy_install -U pip virtualenv')

@_fab.roles('web')
def do_perllibs():
    """Install Perl libraries that are not in apt"""
    perllibs = (
        'http://search.cpan.org/CPAN/authors/id/J/JG/JGOLDBERG/Text-Levenshtein-0.05.tar.gz',
        'http://search.cpan.org/CPAN/authors/id/R/RH/RHOOPER/HTTP-Lite-2.1.6.tar.gz',
        'http://search.cpan.org/CPAN/authors/id/L/LD/LDS/GD-2.44.tar.gz')

    with _fab.hide('stdout', 'stderr'):

        for lib in perllibs:
            file = os.path.basename(lib)

            with _fab.cd('/tmp'):
                _fab.run('wget %s' % lib)
                _fab.run('tar xf %s' % file)

                with _fab.cd(file.strip('.tar.gz')):
                    _fab.run('perl Makefile.PL')
                    _fab.run('make')
                    _fab.sudo('make install')

@_fab.roles('web')
def do_legacyperl(version='HEAD'):
    """Install and configure the legacyperl codebase

    This will also create :file:`trn.cfg`.

    """
    tempdir = tempfile.mkdtemp()
    clone = os.path.join(tempdir, 'legacyperl')
    tarball = os.path.join(tempdir, 'cgi-bin.tar')

    _fab.local('git clone git+ssh://git@code.mydomain.com/legacyperl %s'\
            % os.path.join(tempdir, 'legacyperl'))

    with _fab.cd(clone):
        _fab.local('git checkout -b rewrite origin/rewrite')
        _fab.local('git archive --prefix="cgi-bin/" --output %(tarball)s '\
                '%(version)s' % locals())

    _fab.put(tarball, '/tmp')
    shutil.rmtree(tempdir)

    _fab.sudo('mkdir -p %(PATH)s' % _fab.env)

    with _fab.cd(_fab.env.get('PATH')):
        _fab.sudo('tar xf /tmp/cgi-bin.tar')

    # FIXME: upload_template isn't setting the right permissions
    fabric.contrib.files.upload_template(
        '%(TMPL)s/trn.cfg.tmpl' % _fab.env,
        '%(PATH)s/cgi-bin/trn.cfg' % _fab.env,
        context=_fab.env,
        use_sudo=True)
    _fab.sudo('chown root:root %(PATH)s/cgi-bin/trn.cfg' % _fab.env)
    _fab.sudo('chmod 644 %(PATH)s/cgi-bin/trn.cfg' % _fab.env)

def _vbox_state(guest=_fab.env.get('GUEST')):
    """Get the state of the specified machine."""
    vminfo = subprocess.Popen(['VBoxManage', '-q', 'showvminfo', guest,
        '--machinereadable'], stdout=subprocess.PIPE)
    result = filter(lambda x: 'VMState="' in x, vminfo.stdout.readlines()).pop()
    return result.split('"')[1]

def _vbox_start(startvm=True, progress=False,
        guest=_fab.env.get('GUEST'),
        headless=_fab.env.get('HEADLESS')):
    """Provide a mechanism for guessing when a VBox machine is up and running.

    This is currently gagued by when ssh becomes available and requires that
    port forwarding has already been established. Will hang the script until
    the VM is available.

    """
    if startvm:
        if _str2bool(headless):
            _local(['VBoxManage', '-q', 'startvm', guest, '--type', 'vrdp'])
        else:
            _local(['VBoxManage', '-q', 'startvm', guest])

    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3.0)
            s.connect(('localhost', int(_fab.env['SSH_PORT'])))
            response = s.recv(1024)
        except (socket.error, socket.timeout), e:
            pass
        else:
            if 'SSH' in response:
                break

            if progress:
                sys.stdout.write('.')
                sys.stdout.flush()

            time.sleep(3)
        finally:
            s.close()

def _vbox_stop(stopvm=True, guest=_fab.env.get('GUEST')):
    """Provide a mechanism for guessing when a VBox machine has been stopped.
    Will hang the script until the VM has been stopped.

    """
    if stopvm:
        _local(['VBoxManage', '-q', 'controlvm', guest, 'acpipowerbutton'])

    while True:
        state = _vbox_state(guest=guest)

        if state in ['stopped', 'poweroff', 'saved']:
            break

        time.sleep(3)

def _vbox_checkreqs():
    """Check the local system for all required software."""
    errors = []

    with _fab.hide('running'):
        with _fab.settings(warn_only=True):
            vbox_ver = _fab.local('VBoxManage --version')
            git_ver = _fab.local('git --version').strip('git version ')

            try:
                vbox_ver = distutils.version.LooseVersion(vbox_ver)
                git_ver = distutils.version.LooseVersion(git_ver)
            except ValueError:
                errors.append("""\
                    You must have git and VirtualBox installed before running
                    this script.
                    """)
            else:
                if vbox_ver < _fab.env['VBOX_MIN_VER']:
                    errors.append("""\
                    You must have at least VirtualBox version %(VBOX_MIN_VER)s.
                    """ % _fab.env)

                if git_ver < _fab.env['GIT_MIN_VER']:
                    errors.append("""\
                        You must have at least git version %(GIT_MIN_VER)s.
                        """ % _fab.env)

    if errors:
        for error in errors:
            _write(error, desc='stderr')

        _fab.abort("Software requirements not met.")

def vbox(guest=_fab.env.get('GUEST'),
        revert=_fab.env.get('REVERT'),
        headless=_fab.env.get('HEADLESS')):
    """Start/stop the development virtual machine

    Usage::

        fab vbox[:guest=somename]

    A shortcut to set up the right port-forwarding, mount the isilon, and start
    the virtual machine.
    
    """
    state = _vbox_state(guest=guest)

    if state in ['running', 'paused']:
        # Stop the machine if it is running.
        if _str2bool(revert):
            # Revert to the most recent snapshot
            _local(['VBoxManage', 'discardstate', guest])
        else:
            # Save the current state
            _local(['VBoxManage', '-q', 'controlvm', guest, 'savestate'])

        _write("Stopped.\n")

    else:
        # Start the machine if it is stopped.
        vbox_portfwd(guest=guest)
        _vbox_start(guest=guest, headless=headless)

        _write("""\
            %(guest)s is now running.

            You may surf to %(URI)s or ssh to ssh://localhost:%(SSH_PORT)s.

            """ % dict(locals(), **_fab.env))

def vbox_portfwd(guest=_fab.env.get('GUEST')):
    """Configure VBox port forwarding for ssh and http(s)

    Usage::

        vbox_portfwd[:guest=somename]

    This allows you to easily access the services hosted on the VirtualBox
    Guest OS from your local Host machine.

    .. warning::

        The virtual machine must be stopped and started before forwarding
        becomes available.

    """
    fwd_ports = (
        ('ssh', '22', _fab.env['SSH_PORT']),
        ('http', '8080', _fab.env['HTTP_PORT']),
        ('https', '443', '4433'))

    cmd = subprocess.list2cmdline([
        'VBoxManage', '-q', 'setextradata', guest,
        'VBoxInternal/Devices/pcnet/0/LUN#0/Config/%s/%s', '%s'])

    # Stop the VM first
    with _fab.settings(warn_only=True):
        _local(['VBoxManage', '-q', 'controlvm', guest, 'savestate'])

    for name, guest, host in fwd_ports:
        _fab.local(cmd % (name, 'HostPort', host))
        _fab.local(cmd % (name, 'GuestPort', guest))
        _fab.local(cmd % (name, 'Protocol', 'TCP'))

@_fab.hosts(', '.join(LOCALHOST))
def vbox_bootstrap(guest=_fab.env.get('GUEST'), force=False,
        version=_fab.env.get('VERSION')):
    """Create a new VirtualBox Ubuntu enviroment

    Usage::

        vbox_bootstrap[:guest=somename,force=yes]

    This will create a new VBox machine, install Ubuntu on it, and set up the
    necessary port forwarding for you to access it from your local machine.

    This script will delete an existing VM if you pass ``force=yes``.

    """
    _vbox_checkreqs()

    try:
        sys_prop = subprocess.Popen(['VBoxManage', '-q', 'list',
            'systemproperties'], stdout=subprocess.PIPE)

        result = filter(lambda x: 'Default hard disk folder' in x,
                sys_prop.stdout.readlines()).pop()

        path = [i.strip() for i in result.split('/')]
        path.pop(0)

        VBOX_DIR = os.path.join('/', *path)
    except IndexError:
        _fab.abort("Could not determine VirtualBox info. Is it installed?")

    # When you update this URL for new Ubuntu releases, be sure to also make
    # sure the preseed.cfg file is still up-to-date.
    # https://help.ubuntu.com/8.04/installation-guide/example-preseed.txt
    DEB_URL = 'http://mirrors.xmission.com/ubuntu-cd/8.04/ubuntu-8.04.3-server-i386.iso'
    DEB_ISO = os.path.basename(DEB_URL)
    DEB_FILE = os.path.join(VBOX_DIR, DEB_ISO)

    # Roundabout, but crossplatform, way to retrive local ip address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('google.com', 80))
    IP = s.getsockname()[0]
    if not IP:
        IP = _fab.prompt("I could not guess your IP address. Enter it now:")

    # Easily map keystrokes to VBoxManage scancodes
    scancodes = {
        'esc': '01', 'tab': '0f', 'enter': '1c', 'space': '39',
        'backspace': '0e', 'lshiftd': '2a', 'lshiftu': 'aa',
        'up': '48', 'down': '50', 'right': '4b', 'left': '4d',

        'A': '1e', 'B': '30', 'C': '2e', 'D': '20', 'E': '12', 'F': '21',
        'G': '22', 'H': '23', 'I': '17', 'J': '24', 'K': '25', 'L': '26',
        'M': '32', 'N': '31', 'O': '18', 'P': '19', 'Q': '10', 'R': '13',
        'S': '1f', 'T': '14', 'U': '16', 'V': '2f', 'W': '11', 'X': '2d',
        'Y': '15', 'Z': '2c',

        '1': '02', '2': '03', '3': '04', '4': '05', '5': '06',
        '6': '07', '7': '08', '8': '09', '9': '0a', '0': '0b',

        'F1': '3b', 'F2': '3c', 'F3': '3d', 'F4': '3e', 'F5': '3f',
        'F6': '40', 'F7': '41', 'F8': '42', 'F9': '43', 'F10': '44',

        ';': '27', "'": '28', '`': '29', '/': '35', '=': '0d', '-': '0c',
        '.': '34', ' ': '39',

        ':': '2a 27 aa', '"': '2a 28 aa', '~': '2a 29 aa', '?': '2a 35 aa',
        '+': '2a 0d aa', '_': '2a 0c aa'}

    ### Create the VMs
    if '"%s"' % guest in _local(['VBoxManage', '-q', 'list', 'vms']):
        if _str2bool(force) and fabric.contrib.console.confirm(textwrap.dedent("""\
                Are you sure you want to completely delete the virtual machine
                and associated disk image for the guest %s?""" % guest),
                default=False):

            with _fab.settings(warn_only=True):
                # Make sure the machine isn't running or saved
                _local(['VBoxManage', 'controlvm', guest, 'poweroff'])
                _local(['VBoxManage', 'discardstate', guest])

                # Get list of snapshots and delete them
                vminfo = subprocess.Popen(['VBoxManage', '-q', 'showvminfo',
                    guest, '--machinereadable'], stdout=subprocess.PIPE)
                snapshots = filter(lambda x: 'SnapshotUUID' in x,
                        vminfo.stdout.readlines())

                for snapshot in snapshots:
                    _local(['VBoxManage', 'snapshot', guest, 'delete',
                        snapshot.split('"')[1]])

                # Eject the CD
                _local(['VBoxManage', '-q', 'storageattach', guest,
                    '--storagectl', 'IDE Controller', '--port', '0',
                    '--device', '0', '--medium', 'none'])

                # Delete the machine
                _local(['VBoxManage', '-q', 'storageattach', guest,
                    '--storagectl', guest, '--port', '0', '--device', '0',
                    '--medium', 'none'])
                _local(['VBoxManage', '-q', 'storagectl', guest, '--name',
                    guest, '--remove'])
                _local(['VBoxManage', '-q', 'unregistervm', guest, '--delete'])
                _local(['VBoxManage', '-q', 'closemedium', 'disk', '%s.vdi' % guest])

                # Delete the hard disk
                try:
                    os.remove(os.path.join(VBOX_DIR, '%s.vdi' % guest))
                except OSError:
                    pass
        else:
            _fab.abort("The VM %s is already registered." % guest)

    _local(['VBoxManage', '-q', 'createvm', '--name', guest, '--register',
        '--ostype', 'Ubuntu'])
    _local(['VBoxManage', '-q', 'createhd', '--filename', '%s.vdi' % guest,
        '--size', '10240'])
    _local(['VBoxManage', '-q', 'storagectl', guest, '--name', guest, '--add',
        'sata'])
    _local(['VBoxManage', '-q', 'storageattach', guest, '--storagectl', guest,
        '--port', '0', '--device', '0', '--type', 'hdd', '--medium',
        '%s.vdi' % guest])

    # Set port forwarding early so we can tell when the install is done
    vbox_portfwd(guest=guest)

    ### Download Ubuntu & register with VBox's Media Manager
    if not DEB_ISO in _local(['VBoxManage', '-q', 'list', 'dvds']):
        def dl_progress(count, blockSize, totalSize):
            """Show download progress in percent."""
            percent = int(count*blockSize*100/totalSize)
            if count % 10 == 0:
                sys.stdout.write('\rDownloading Ubuntu' + "...%d%%" % percent)
                sys.stdout.flush()

        destination = os.path.join(VBOX_DIR, DEB_FILE)
        urllib.urlretrieve(DEB_URL, destination, reporthook=dl_progress)
        _local(['VBoxManage', '-q', 'openmedium', 'dvd', DEB_FILE])

    # Attach Ubuntu to the VM
    with _fab.settings(warn_only=True):
        _local(['VBoxManage', '-q', 'storagectl', guest, '--name',
            'IDE Controller', '--add', 'ide'])
        _local(['VBoxManage', '-q', 'storageattach', guest, '--storagectl',
            'IDE Controller', '--port', '0', '--device', '0', '--type',
            'dvddrive', '--medium', DEB_FILE])

    ### Start the virtual machine
    vbox_pid = subprocess.Popen(['VBoxManage', '-q', 'startvm', guest])

    # Wait for the VM to start up before sending keycodes
    time.sleep(5)
    sequence = []

    for c in ['enter', 'F6']:
        sequence.append(scancodes.get(c))

    for c in range(80):
        sequence.append(scancodes.get('backspace'))

    # Ubuntu's preseed is awful and doesn't get loaded until late in the
    # install process. All these options are necessary for a headless install.
    # (In contrast, Debian only needs the preseed/url directive.)
    for c in ('preseed/url=http://%(IP)s:8000/preseed.cfg '\
            'auto=true '\
            'console-setup/layoutcode=us '\
            'locale=en_US.UTF-8 '\
            'console-setup/charmap=UTF-8 '\
            'netcfg/get_hostname=ubuntu '\
            'pkgsel/language-pack-patterns= '\
            'pkgsel/install-language-support=false '\
            'initrd=/install/initrd.gz' % locals()).upper():
        sequence.append(scancodes.get(c, 'XXX'))

    sequence.append(scancodes.get('enter'))
    keycodes = " ".join(sequence)

    # VBox seems to have issues with sending the scancodes as one big
    # .join()-ed string. It seems to get them out or order or ignore some.
    # A workaround is to send the scancodes one-by-one.
    for keycode in keycodes.split(' '):
        with _fab.hide('running'):
            _local(['VBoxManage', '-q', 'controlvm', guest, 'keyboardputscancode',
                keycode])

    ### Start a local webserver to serve the preseed script to the installer
    # I don't think it's possible to manually specify the root dir
    OLDPWD = os.path.abspath(os.path.curdir)
    os.chdir(_fab.env.get('TMPL'))
    httpd = BaseHTTPServer.HTTPServer(('', 8000),
            SimpleHTTPServer.SimpleHTTPRequestHandler)
    httpd.handle_request()
    os.chdir(OLDPWD)

    ### Wait for the install to finish
    sys.stdout.write("\n\nUbuntu is now installing. This may take a while.")
    sys.stdout.flush()
    _vbox_start(guest=guest, startvm=False, progress=True)

    ### Eject the CD
    _vbox_stop(guest=guest)

    _local(['VBoxManage', '-q', 'storageattach', guest, '--storagectl',
        'IDE Controller', '--port', '0', '--device', '0', '--medium',
        'none'])

    _vbox_start(guest=guest)

    ### Snapshot the clean installation
    _local(['VBoxManage', '-q', 'snapshot', guest, 'take', 'Pristine',
        '--description', 'Clean installation, no extra software.'])

    _write("""\

            Ubuntu has been installed. The system will now be configured.

            You will be prompted for the ssh password of the devenv user. The
            password is:

                cards

            (If you are running ssh-agent you may also be prompted for your
            passphrase -- just hit enter.)

            If the configuration process is interrupted after this point you
            may resume it via:

                fab vbox_postinstall

            """)
    ### Configure the new system
    vbox_postinstall(guest=guest, version=version)

@_fab.hosts(', '.join(LOCALHOST))
def vbox_postinstall(guest=_fab.env.get('GUEST'), version=_fab.env.get('VERSION')):
    """Configure an existing virtual machine."""
    # Ignore the ssh known_hosts file here because there may already be an
    # entry for localhost:2222 that was set up for another virtual machine and
    # we don't want the script to die just because of that.
    with _fab.settings(disable_known_hosts=True):
        do_sshkey()

    # Make an entry in the guest hosts file so it knows who we think it is
    fabric.contrib.files.append(
            '127.0.0.1       %(DOMAIN)s  ubuntu' % _fab.env,
            '/etc/hosts',
            use_sudo=True)

    ### Configure sudo to not require a password
    # fabric.contrib.files.uncomment('/etc/sudoers', '%sudo', use_sudo=True)
    # fabric.contrib.files.comment('/etc/sudoers', '%admin', use_sudo=True)

    ### Install required software
    do_metadeb()

    ### Install required Python & Perl libs
    do_pythonlibs()
    do_perllibs()

    ### Set up local database
    # Create the database
    do_postgres()

    # Disable local password auth
    fabric.contrib.files.sed('/etc/postgresql/8.3/main/pg_hba.conf',
        'ident sameuser', 'trust', 'all\s*all', use_sudo=True)

    # Populate local database with sample data
    activate = "source %(PATH)s/bin/activate" % _fab.env

    with _fab.cd('%(PATH)s/project' % _fab.env):
        _fab.sudo(activate + ' && ' + './manage.py loaddata '\
                'sample_users categories sample_sendablecards countries')

    ### Install legacy Perl code
    do_legacyperl()

    ### Do initial deploy of Python code
    deploy(version=version)

    ### Configure Apache
    # Create the vhost
    do_apache_vhost()

    # Set verbose logging
    fabric.contrib.files.sed(
        '/etc/apache2/sites-available/mydomain.com',
        'LogLevel warn', 'LogLevel info', use_sudo=True)

    # Make Apache listen on port 8080 because that solves a few problems trying
    # to translate from 8080 on the guest to 80 on the host
    fabric.contrib.files.append('Listen %(HTTP_PORT)s' % _fab.env,
            '/etc/apache2/ports.conf', use_sudo=True)

    ### Restart the virtual machine to cement any new settings/services
    _vbox_stop(guest=guest)
    _vbox_start(guest=guest)

    ### Snapshot the configured installation so users feel free to mess with it
    _local(['VBoxManage', '-q', 'snapshot', guest, 'take', 'Configured',
        '--description', 'Fully configured system.'])

    ### Stop the machine and display success instructions
    _local(['VBoxManage', '-q', 'controlvm', guest, 'savestate'])

    _write("""\

        *********************************************************************
        Done!

        You should make a new entry in your hosts file:

            127.0.0.1               %(DOMAIN)s

        Your development environment is now fully configured. You may start it,
        stop it, or switch between multiple virtual machines by running:

            fab vbox

        For all Fabric commands run:

            fab --list

        And for detailed usage for a particular command run:

            fab --display commandname

        *********************************************************************
        """ % _fab.env)

@_fab.hosts(', '.join(LOCALHOST))
def vbox_clone(guest=_fab.env.get('GUEST'), clone='mydevenv2'):
    """Clone an existing virtual machine

    Usage::

        vbox_clone[:guest=somename,clone=someothername]

    This command may be useful to avoid a lengthy install process if you
    already have an existing clean installation.

    .. note::

        Cloning an exisiting VirtualBox machine will not carry over snapshots,
        current state, or any custom settings. Only the hard-disk is cloned.

    """
    _local(['VBoxManage', '-q', 'clonehd', '%s.vdi' % guest,
        '%s.vdi' % clone, '--remember'])
    _local(['VBoxManage', '-q', 'createvm', '--name', clone, '--register',
        '--ostype', 'Ubuntu'])
    _local(['VBoxManage', '-q', 'storagectl', clone, '--name', clone, '--add',
        'sata'])
    _local(['VBoxManage', '-q', 'storageattach', clone, '--storagectl', clone,
        '--port', '0', '--device', '0', '--type', 'hdd', '--medium',
        '%s.vdi' % clone])


##### Deployment Functions
###############################################################################
@_fab.roles('web')
def restart(hard=False):
    """Restart Apache

    By default performs a graceful restart.

    """
    if not _str2bool(hard):
        _fab.sudo('/etc/init.d/apache2 reload')
    else:
        _fab.sudo('/etc/init.d/apache2 restart')

@_fab.roles('web')
def deploy(version=_fab.env.get('VERSION'), test=False):
    """Deploy a tarball of the myrepo codebase

    Usage::

        deploy[:version=somebranch]
        deploy[:version=ad8d524ab8ad]

    The code is deployed to a timestamped directory to allow for quick and easy
    rollbacks to previous versions. The timestamped directory is then symlinked
    to the expected destination directory name to make the code live.

    Version can be set to any version identifier that git can handle (revision,
    tag, head, branch).

    """
    ### Run the test suite first and cancel the deploy if it fails
    # TODO: since our test suite is in bad shape, this is disabled by default.
    # we need to get to a position where this can be enabled by default
    if _str2bool(test):
        do_tests()

    ### Put the code on the server
    # Make a temporary timestamped directory
    tempdir = tempfile.mkdtemp()
    timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H%M%S')
    filename = 'mycode-%s.tar' % timestamp
    basename = filename.strip('.tar')
    fullpath = os.path.join(tempdir, filename)

    # Create a tarball of the code
    cmd = _get_vcs_archive_cmd()
    _fab.local(cmd % locals())

    # Put the code on the server
    _fab.put('%(fullpath)s' % locals(), '/tmp')

    # Untar the archive and symlink the timestamped directory for easy rollback
    with _fab.cd(_fab.env.get('PATH')):
        _fab.sudo('tar xf /tmp/%(filename)s' % locals())
        _fab.sudo('ln -sfn %(basename)s mycompany' % locals())
        _fab.sudo('ln -sfn mycompany/src/mycompany project' % locals())
        restart()

    # Clean up
    _fab.run('rm /tmp/%(filename)s' % locals())
    shutil.rmtree(tempdir)

    ### Create and populate the virtualenv
    # NOTE: BASELINE simulates --no-site-packages on mod_wsgi.
    # http://code.google.com/p/modwsgi/wiki/VirtualEnvironments
    _fab.sudo('mkdir -p %(PATH)s' % _fab.env)
    _fab.sudo('virtualenv --no-site-packages /var/www/BASELINE')

    ### Make a symlink for the pre-Fabric location so old code doesn't break
    # until those hardcoded paths can be fixed
    _fab.sudo('ln -sfn %(PATH)s/mycompany /var/www/myrepo' % _fab.env)

    ### Run pip to populate the virtualenv with third-party libs
    with _fab.hide('stdout'):
        _fab.put('../../REQUIREMENTS.txt', '/tmp')
        _fab.sudo('virtualenv --no-site-packages %(PATH)s' % _fab.env)
        _fab.sudo('pip install -E %(PATH)s -r /tmp/REQUIREMENTS.txt' % _fab.env)
        _fab.run('rm /tmp/REQUIREMENTS.txt')

    ### Make a server-writable MEDIA_ROOT
    _fab.sudo('mkdir -p %(MEDIA_ROOT)s' % _fab.env)
    _fab.sudo('chgrp -R www-data %(MEDIA_ROOT)s' % _fab.env)
    _fab.sudo('chmod g+w,g+s %(MEDIA_ROOT)s' % _fab.env)

    ### The static media should be available from MEDIA_ROOT
    with _fab.cd(_fab.env.get('MEDIA_ROOT')):
        _fab.sudo('ln -sfn ../mycompany/htdocs/css')
        _fab.sudo('ln -sfn ../mycompany/htdocs/javascript')

    ### Put the Django project and system-level libraries on the PYTHONPATH
    with _fab.cd('%(PATH)s/lib/python2.5/site-packages' % _fab.env):
        _fab.sudo('ln -sfn ../../../project mycompany')

        # Put system-level libraries on the virtualenv PYTHONPATH
        for lib in ('psycopg2', 'PIL', 'mx'):
            _fab.sudo('ln -sfn /usr/lib/python2.5/site-packages/%s' % lib)

        # Ug! Stupid Ubuntu feels the need to customize *everything*.
        for lib in ('MySQLdb', '_mysql.so', '_mysql_exceptions.py'):
            _fab.sudo('ln -sfn /var/lib/python-support/python2.5/%s' % lib)

    ### Upload local_settings
    fabric.contrib.files.upload_template(
        '%(TMPL)s/local_settings.py.tmpl' % _fab.env,
        '%(PATH)s/project/local_settings.py' % _fab.env,
        context=_fab.env,
        use_sudo=True)
    # FIXME: upload_template isn't setting the right permissions
    _fab.sudo('chown root:root %(PATH)s/project/local_settings.py' % _fab.env)
    _fab.sudo('chmod 644 %(PATH)s/project/local_settings.py' % _fab.env)

    # FIXME: Hack. django-compress requires rw access to these files but does
    # not appear to actually write anything. Either way, it is desirable to
    # keep server-writable directories *out* of the repo entirely; this needs
    # to be cleaned up.
    _fab.sudo('chgrp -R www-data %(PATH)s/mycompany/htdocs' % _fab.env)
    _fab.sudo('chmod -R g+w %(PATH)s/mycompany/htdocs' % _fab.env)

    ### Run Django syncdb to create/update the database
    activate = "source %(PATH)s/bin/activate" % _fab.env

    with _fab.cd('%(PATH)s/project' % _fab.env):
        _fab.sudo(activate + ' && ' + './manage.py syncdb --noinput')

    ### Restart the web server
    restart()

@_fab.roles('web')
def rollback(version='list'):
    """Rollback to a previous deployment

    Usage::

        rollback[:version=2009-12-31T2359]
    
    By default this will only list what previous deployments are available. To
    specify a version to rollback to pass the ``version`` argument.

    """
    with _fab.hide('running', 'stdout', 'stderr'):
        previous = [
            os.path.basename(i).strip('mycompany-')
            for i in _fab.run('ls -rd %(PATH)s/mycompany-20*' % _fab.env
                ).split('\n')]

    if version == 'list':
        _write("""\
            Please enter the date of a previous deployment to rollback:

            """)
        sys.stdout.write('\n'.join(previous))
        sys.stdout.write('\n\n')
        sys.stdout.flush()
        sys.exit()
    else:
        if not version in previous:
            _fab.abort('The version you specified does not exist.')

    with _fab.cd(_fab.env.get('PATH')):
        _fab.sudo('ln -sfn mycompany-%s mycompany' % version)
        restart()

@_fab.roles('web')
def rsync():
    """Synchronise local files with remote files

    In lieu of a full :func:`deploy`, this command will use :command:`rsync` to
    transfer any files that have changed in the local project directory. This
    is useful for front-end development when creating tons of small commits
    would be annoying.

    """
    fabric.contrib.project.rsync_project(
            '%(PATH)s' % _fab.env, os.path.dirname(__file__))