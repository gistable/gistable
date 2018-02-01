from fabric.api import *
from fabric.contrib.console import confirm
import tempfile
import re

PROJ_VER='4.8.0'
GEOS_VER='3.3.3'
GDAL_VER='1.9.0'

PROJ_PATH='/usr/local/proj/' + PROJ_VER
GEOS_PATH='/usr/local/geos/' + GEOS_VER
GDAL_PATH='/usr/local/gdal/' + GDAL_VER

FILEGDBAPI_FILE = 'FileGDB_API_1_2-64.tar.gz'
FILEGDBAPI_LOCATION = 'http://dl.dropbox.com/u/4779803/%s' % (FILEGDBAPI_FILE,)

TEMP_DIR = '/tmp/'

PROJ_ROOT = '/srv/mydjangoproject'
PYTHON_INTERPRETER = '/srv/myvirtualenv/bin/python'

def macpro():
    env.hosts = ['10.0.0.21']
    env.user = env.deploy_user = 'rburhum'
    env.directory = '/srv/myvirtualenv'
    env.activate = '/srv/myvirtualenv/bin/activate'
    env.password = 'mypassword'

def virtualenv(command):
    with cd(env.directory):
        sudo('source ' + env.activate + ' && '  + command, user=env.deploy_user)

def manage_py(command):
    run(PYTHON_INTERPRETER + ' ' + PROJ_ROOT + '/manage.py '  + command)

def deploy():

    with cd(PROJ_ROOT):
        run('hg pull')
        run('hg update')

        virtualenv('pip install -r ' + PROJ_ROOT + '/pip-req.txt')

        manage_py('syncdb --migrate')
        manage_py('collectstatic -l --noinput')

    sudo('/etc/init.d/apache2 restart')
    sudo('/etc/init.d/celeryd restart')
    sudo('/etc/init.d/celeryevcam restart')


def install_filegdb():
    with cd(TEMP_DIR):
        proj_filename = 'proj-%s.tar.gz' % PROJ_VER
        geos_filename = 'geos-%s.tar.bz2' % GEOS_VER
        gdal_filename = 'gdal-%s.tar.gz' % GDAL_VER

        run('wget -c %s' % (FILEGDBAPI_LOCATION,))
        run('wget -c http://download.osgeo.org/proj/%s' % (proj_filename,))
        run('wget -c http://download.osgeo.org/geos/%s' % (geos_filename,))
        run('wget -c http://download.osgeo.org/gdal/%s' % (gdal_filename,))


        run('tar xzf %s' % (FILEGDBAPI_FILE,))
        run('tar xzf %s' % (proj_filename,))
        run('tar xjf %s' % (geos_filename,))
        run('tar xzf %s' % (gdal_filename,))

        #install FILEGDB API based on current ESRI defaults
        sudo('rm -rf /usr/local/FileGDB_API 2>/dev/null')
        sudo('mv FileGDB_API /usr/local/FileGDB_API')
        #sudo('echo \"/usr/local/FileGDB_API/lib\"  > /etc/ld.so.conf.d/filegdb.conf')

        with settings(warn_only=True):
            sudo('ln -s /usr/local/FileGDB_API/lib/* /usr/local/lib/')
            #temp fix for filegdb bug that got fixed in trunk (after 1.9)
            #fix start
            sudo('ln -s /usr/local/lib/libfgdbunixrtl.so /usr/local/lib/libfgdblinuxrtl.so')
            #fix end

        sudo('ldconfig')

        with cd('proj-%s' % PROJ_VER):
            run('./configure')
            run('make')
            sudo('make install')
            sudo('ldconfig')

        with cd('geos-%s' % GEOS_VER):
            run('./configure')
            run('make')
            sudo('make install')
            sudo('ldconfig')

        with cd('gdal-%s' % GDAL_VER):
            run('./configure --with-python --with-fgdb=/usr/local/FileGDB_API')
            run('make')
            sudo('make install')
            sudo('ldconfig')