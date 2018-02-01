from __future__ import with_statement
from fabric.api import env, run, settings, hide
from fabric.decorators import hosts, runs_once

venv = "/home/websites/.virtualenvs/twtv3/"

env.user = 'webdev'
env.hosts = [
    '192.168.1.10', 
    '192.168.1.11', 
    '192.168.1.12', 
    '192.168.1.13', 
]

def _get_package_list():
    """
    Get the list of currently installed packages and versions via pip freeze
    """
    with settings(
        hide('warnings', 'running', 'stdout', 'stderr'),
        warn_only=True
    ):
        return run("%sbin/pip freeze -l" % venv)

def _process_packages(packages):
    """
    Convert the packages datastructure into the multiple versions and missing
    servers lists and output the result
    """
    multi_versions = {}
    missing_servers = []
    for package, versions in packages.items():
        if len(versions.keys()) > 1:
            # There is more than one version installed on the servers
            multi_versions[package] = versions
        elif len(versions[versions.keys()[0]]) != len(env.hosts):
            # The package is not installed on all the servers
            missing_hosts = set(env.hosts) - set(versions[versions.keys()[0]])
            missing_servers.append(
                "%s: %s" % (package, ", ".join(missing_hosts))
            )
    if missing_servers or multi_versions:
        print ""
        print "Packages out-of-sync:"
    if multi_versions:
        print ""
        print "Multiple versions found of these packages:"
        for package, versions in multi_versions.items():
            print package
            for ver, servers in versions.items():
                print "  %s: %s" % (ver, ", ".join(servers))
    if missing_servers:
        print ""
        print "These packages are missing on these servers:"
        for item in missing_servers:
            print item

@runs_once
def check_package_versions():
    """
    Check the versions of all the packages on all the servers and print out
    the out of sync packages
    """
    packages = {}
    for host in env.hosts:
        with settings(host_string=host):
            print "Getting packages on %s" % host
            result = _get_package_list()
            pkg_list = result.splitlines()
            for package in pkg_list:
                if package.startswith("-e"):
                    version, pkg = package.split("#egg=")
                else:
                    pkg, version = package.split("==")
                if pkg not in packages:
                    packages[pkg] = {}
                if version not in packages[pkg]:
                    packages[pkg][version] = []
                packages[pkg][version].append(host)
    _process_packages(packages)