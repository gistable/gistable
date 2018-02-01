import os
import re

from fabric.api import *
import yaml

"""
Base configuration
"""
# Ubuntu
if os.path.exists('/usr/share/tilemill'):
    env.tilemill_path = '/usr/share/tilemill'
    env.tilemill_projects = '/usr/share/mapbox/project'
    env.node_path = '/usr/bin/node'
# OSX
else:
    env.tilemill_path = '/Applications/TileMill.app/Contents/Resources'
    env.tilemill_projects = '~/Documents/MapBox/project'
    env.node_path = '%(tilemill_path)s/node' % env

"""
Environments
"""
def production():
    """
    Work on production environment
    """
    env.settings = 'production'
    env.s3_buckets = ['media.apps.chicagotribune.com', 'maps1.tribapps.com', 'maps2.tribapps.com', 'maps3.tribapps.com', 'maps4.tribapps.com']
    env.acl = 'acl-public'

def staging():
    """
    Work on staging environment
    """
    env.settings = 'staging'
    env.s3_buckets = ['media-beta.tribapps.com']
    env.acl = 'acl-private'

def map(name):
    """
    Select map to work on.
    """
    env.map = name

"""
Commands - deployment
"""
def _deploy_to_s3(concurrency):
    """
    Deploy tiles to S3.
    """
    env.concurrency = concurrency

    # Deploy to many buckets (multi-dns-head mode)
    for bucket in env.s3_buckets:
        env.s3_bucket = bucket    
        local('ivs3 %(map)s/tiles %(s3_bucket)s/%(project_name)s/%(map)s --%(acl)s -c %(concurrency)s' % env)

def deploy(concurrency=32):
    """
    Deploy a map. Optionally takes a concurrency parameter indicating how many files to upload simultaneously.
    """
    require('settings', provided_by=[production, staging])
    require('map', provided_by=[map])
    
    _deploy_to_s3(concurrency)

def deploy_browser():
    """Update and deploy the browser.html file."""
    require('settings', provided_by=[production, staging])
    local("./make_layer_selector.py")
    local('s3cmd -P --guess-mime-type put browser.html s3://%(s3_bucket)s/%(project_name)s/browser.html' % env)
    local('s3cmd -P --guess-mime-type put logo.png s3://%(s3_bucket)s/%(project_name)s/logo.png' % env)

"""
Commands - processing
"""
def _update_config_from_tilemill():
    """
    Copy the latest configuration from TileMill to the local directory.
    """
    if not os.path.exists('%(map)s' % env):
        os.mkdir('%(map)s' % env)

    local('cp %(tilemill_projects)s/%(map)s/*.mss %(map)s' % env)
    local('cp %(tilemill_projects)s/%(map)s/*.mml %(map)s' % env)

def _update_config_from_project():
    """
    Copy the latest configuration to TileMill from the local directory.
    """
    if not os.path.exists('%(tilemill_projects)s/%(map)s/' % env):
        os.mkdir(os.path.expanduser('%(tilemill_projects)s/%(map)s/' % env))

    local('cp %(map)s/*.mss %(tilemill_projects)s/%(map)s/' % env)
    local('cp %(map)s/*.mml %(tilemill_projects)s/%(map)s/' % env)
    
def _rewrite_paths():
    """
    Rewrite carto configuration so that shapefile references point to the local shapefiles directory.
    """
    contents = None 

    with open('%(map)s/%(map)s.mml' % env, 'r') as f:
        contents = f.read()

    shapefile_path = os.path.join('..', 'shapefiles')
    contents = re.sub('(?<=file"\:\s")(.*)(?=/.*/.*.shp")', shapefile_path, contents) 

    with open('%(map)s/%(map)s.mml' % env, 'w') as f:
        f.write(contents)

def _carto_to_mapnik():
    """
    Convert carto styles to mapnik configuration.
    """
    # Convert tilemill config to mapnik config
    local('%(tilemill_path)s/node_modules/carto/bin/carto %(map)s/%(map)s.mml > %(map)s/%(map)s.xml' % env)

    # Remove cruft
    local('rm -rf %(map)s/layers' % env)

def _render_tiles(process_count):
    """
    Only render a tile map (does not update configuration).
    """
    env.process_count = process_count

    # Fetch configuration from yaml file
    with open('%(map)s/config.yml' % env, 'r') as f:
        config = yaml.load(f)

    env.update(config)

    command = 'ivtile %(map)s/%(map)s.xml %(map)s/tiles %(max-latitude)s %(min-longitude)s %(min-latitude)s %(max-longitude)s %(min-zoom)s %(max-zoom)s -p %(process_count)s'

    if 'buffer' in config:
        command += ' -b %(buffer)s'

    # Render tiles
    local(command % env)

def setup():
    """
    Run the setup script for a given map.
    """
    require('map', provided_by=[map])
    
    with lcd('%(map)s' % env):
        local('bash setup.sh',capture=False)

def sync():
    """
    Update configuration from the project.
    """
    require('map', provided_by=[map])

    _update_config_from_project()

def update():
    """
    Update configuration from TileMill.
    """
    require('map', provided_by=[map])

    _update_config_from_tilemill()
    _rewrite_paths()
    _carto_to_mapnik()

def render(process_count=1):
    """
    Updates configuration and renders a tile map.
    """
    require('map', provided_by=[map])

    update()
    _render_tiles(process_count)

def mbtiles():
    """
    Uses TileMill to export an mbtiles file for a map (for generating grid files).
    """
    require('map', provided_by=[map])
    
    with open('%(map)s/config.yml' % env, 'r') as f:
        config = yaml.load(f)

    env.update(config)

    with settings(warn_only=True):
        local('rm -rf %(map)s/*.mbtiles' % env)

    local('%(node_path)s %(tilemill_path)s/index.js export --minzoom=%(min-zoom)s --maxzoom=%(max-zoom)s --bbox=%(min-longitude)s,%(min-latitude)s,%(max-longitude)s,%(max-latitude)s %(map)s %(map)s/%(map)s.mbtiles' % env)

def grid():
    """
    Render to mbtiles then extract the grid.
    """
    require('map', provided_by=[map])

    mbtiles()
    
    with settings(warn_only=True):
        local('rm -rf %(map)s/tiles' % env)

    local('/Users/sk/src/mbutil/mb-util %(map)s/%(map)s.mbtiles %(map)s/tmp-tiles' % env)
    local('mv %(map)s/tmp-tiles/1.0.0/%(map)s %(map)s/tiles' % env)
    local('rm -rf %(map)s/tmp-tiles' % env)

"""
Deaths, destroyers of worlds
"""
def shiva_the_destroyer():
    """
    Remove all directories, databases, etc. associated with the application.
    """
    with settings(warn_only=True):
        local('s3cmd del --recursive s3://%(s3_bucket)s/%(project_name)s' % env)
