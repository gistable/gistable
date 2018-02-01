#!/usr/bin/env python
# vim: ts=4:sw=4:expandtab:autoindent:
import os
import sys
import requests
import filecmp
from fabric.context_managers import hide, settings, prefix
from fabric.api import sudo, task, run, cd, env
from fabric.contrib.console import confirm
from fabric.colors import green

def asset_from_release(release):
    asset_url = release['assets'][0]['url']
    filename = release['assets'][0]['name']

    return asset_url, filename


def get_stable_release():
    response = requests.get('https://api.github.com/repos/getredash/redash/releases/latest')

    if response.status_code != 200:
        exit("Failed getting release (status code: %s)." % response.status_code)

    return asset_from_release(response.json())
    

def get_latest_release():
    response = requests.get('https://api.github.com/repos/getredash/redash/releases')

    if response.status_code != 200:
        exit("Failed getting releases (status code: %s)." % response.status_code)

    sorted_releases = filter(lambda r: r['prerelease'], sorted(response.json(), key=lambda release: release['id'], reverse=True))

    latest_release = sorted_releases[0]
    return asset_from_release(latest_release)

@task
def link_to_current(version_name):
    run('sudo ln -nfs /opt/redash/{0} /opt/redash/current'.format(version_name))

@task
def restart_services():
    # We're doing this instead of simple 'supervisorctl restart all' because
    # otherwise it won't notice that /opt/redash/current pointing at a different
    # directory.
    run('sudo /etc/init.d/redash_supervisord restart')


@task
def find_migrations(version_name):
    new_version_path = '/opt/redash/{0}/migrations'.format(version_name)
    current_version_path = '/opt/redash/current/migrations'

    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        compare_command = "diff <(cd {} && find . | sort) <(cd {} && find . | sort)".format(new_version_path, current_version_path)
        result = run(compare_command)

    new_migrations = []
    for line in result.split("\n"):
        if line.startswith("< "):
            new_migrations.append(line.replace("< ./", "").strip())

    if new_migrations:
        print "New migrations to run: "
        print ', '.join(new_migrations)
    else:
        print "No new migrations in this version."

    return new_migrations


def update_requirements(version_name):
    new_requirements_file = '/opt/redash/{}/requirements.txt'.format(version_name)

    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        result = run('diff /opt/redash/current/requirements.txt {}'.format(new_requirements_file))
        new_requirements = result.failed
    
    if new_requirements:
        run('sudo pip install -r {}'.format(new_requirements_file))


@task
def apply_migrations(version_name):
    new_migrations = find_migrations(version_name)
    if new_migrations and confirm("Apply new migrations? (make sure you have backup)"):
        for migration in new_migrations:
            print "Applying {}...".format(migration)
            with cd("/opt/redash/{0}".format(version_name)):
                # Double sudo isn't a mistake here. It's needed on GCE/Debian based installs,
                # that don't allow passwordless sudo -u.
                run("sudo sudo -u redash PYTHONPATH=. bin/run python migrations/{}".format(migration))

@task
def deploy_latest_release(should_link=True, restart=True, stable='True'):
    if stable in ('True', 'true', 'yes'):
        asset_url, filename = get_stable_release()
    else:
        asset_url, filename = get_latest_release()

    # Get file & extract
    version_name = filename.replace('.tar.gz', '')
    print "Deploying version: {}".format(version_name)
    directory_name = version_name

    with cd('/opt/redash'):
        with hide('running', 'stdout', 'stderr'):
            print green("Downloading latest version...")        
            run('sudo wget --header="Accept: application/octet-stream" -O {} {}'.format(filename, asset_url))
            print green("Unpacking...")        
            run('sudo mkdir -p {}'.format(directory_name))
            run('sudo tar -C {} -xvf {}'.format(directory_name, filename))
            print green("Changing ownership to redash...")        
            run('sudo chown redash {}'.format(directory_name))
            print green("Linking .env file...")        
            run('sudo ln -nfs /opt/redash/.env /opt/redash/{0}/.env'.format(directory_name))

    update_requirements(version_name)
    apply_migrations(version_name)

    if should_link:
        link_to_current(version_name)

    if restart:
        restart_services()
