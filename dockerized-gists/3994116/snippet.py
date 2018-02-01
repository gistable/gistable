from fabric.context_managers import cd
from fabric.contrib.files import exists
from fabric.decorators import hosts
from fabric.decorators import task
from fabric.operations import run
from fabric.operations import sudo

PACKAGES = [
    # 'python-mapnik',
    'binutils',
    'build-essential',
    'bzr',
    'coffeescript',
    'curl',
    'emacs23-nox',
    'gettext',
    'git',
    'lessc',
    'libjpeg-dev',
    'lynx-cur',
    'memcached',
    'mercurial',
    'nginx',
    'postgresql-9.1-postgis',
    'python-dev',
    'python-gdal',
    'python-imaging',
    'python-lxml',
    'python-matplotlib',
    'python-psycopg2',
    'python-pyproj',
    'python-pysqlite2',
    'python-scipy',
    'python-setuptools',
    'python-virtualenv',
    'spatialite-bin',
    'subversion',
    'unzip',
    # TODO: check some of 'em for non-X-using packages. Too much is grabbed.

    # For mapnik
    'clang',
    'cpp',
    'g++',
    'libboost-dev',
    'libboost-filesystem-dev',
    'libboost-iostreams-dev',
    'libboost-program-options-dev',
    'libboost-python-dev',
    'libboost-regex-dev',
    'libboost-system-dev',
    'libboost-thread-dev',
    'libcairo2',
    'libcairo2-dev',
    'libcairomm-1.0-1',
    'libcairomm-1.0-dev',
    'libfreetype6',
    'libfreetype6-dev',
    'libgdal1-dev',
    'libgeotiff-dev',
    'libicu-dev',
    'libjpeg-dev',
    'libltdl-dev',
    'libltdl7',
    'libpng-dev',
    'libproj-dev',
    'libsqlite3-dev',
    'libtiff-dev',
    'libtiffxx0c2',
    'libxml2',
    'libxml2-dev',
    'postgresql-9.1',
    'postgresql-9.1-postgis',
    'postgresql-contrib-9.1',
    'postgresql-server-dev-9.1',
    'python-cairo',
    'python-cairo-dev',
    'python-dev',
    'python-gdal',
    'python-nose',
    'python-software-properties',
    'ttf-dejavu',
    'ttf-dejavu-core',
    'ttf-dejavu-extra',
    'ttf-unifont',
    ]


@task
@hosts('vagrant@33.33.33.20')
def initial_setup():
    sudo("apt-get update")
    sudo("apt-get install " + ' '.join(PACKAGES))
    if not exists("tools"):
        run("git clone git@github.com:reinout/tools.git")
    if not exists("/Users"):
        sudo("mkdir /Users")
    if not exists("/Users/reinout"):
        with cd('/Users'):
            sudo("ln -s /home/vagrant reinout")
    with cd('tools'):
        run("virtualenv --system-site-packages .")
        run("bin/pip install . -r requirements.txt")
        run("./install_shell_scripts.sh")

    if not exists("Dotfiles"):
        run("git clone ssh://reinout@vanrees.org/~/git/Dotfiles")
        run("dotfiles --sync --force")

    # Set postgres's passwd to postgres.
    # local all all md5 in pg_hba.conf.
    # buildout user aanmaken.
    # Mapnik installeren. (configure: PREFIX=/usr)
