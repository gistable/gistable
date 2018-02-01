#!/usr/bin/python
#
# This script will provides a reverse-search on Packagist to find which libraries uses a given library package
# as a dependency.
#
# Usage:
# First, you need to fetch dependencies: ./packagist.py --fetch
# After, you can start checking packages: ./packagist.py --package <package-name>
#
# Author: Vincent Composieux <vincent.composieux@gmail.com>

import sys, getopt, os
import json
import requests

def fetch_packages(url = None, page = 0, packages = None):
    """
    This function fetch all Packagist packages and stores them into a JSON file
    """
    if packages == None:
        packages = []

    if url == None:
        url = 'https://packagist.org/packages/list.json'

    request = requests.get(url)
    json = request.json()

    current = 0
    total = len(json['packageNames'])

    for library in json['packageNames']:
        current += 1
        percent = (current * 100) / total
        sys.stdout.write("\r> fetching dependencies of %d out of %s libraries... %d%%\r" % (current, total, percent))
        sys.stdout.flush()

        library_request = requests.get('https://packagist.org/packages/%s.json' % library)
        library_json = library_request.json()

        library_array = {'name': None, 'versions': []}

        if 'package' in library_json:
            library_name = library_json['package']['name']
            versions = library_json['package']['versions']

            if len(versions) > 0:
                for version in versions.keys():
                    items = library_json['package']['versions'][version]

                    library_version = {
                        'version': version,
                        'packages': {'require': [], 'require-dev': [], 'suggest': []}
                    }

                    for type in ['require', 'require-dev', 'suggest']:
                        if type in items:
                            for item in items[type]:
                                library_version['packages'][type].append(item)

                    library_array['versions'].append(library_version)

                library_array['name'] = library_name

                packages.append(library_array)

    if 'next' in json:
        page += 1
        packages = fetch_packages(json['next'] + '&q=', page, packages)

    return packages

def get_package_dependencies(libraries, package):
    """
    This function research for libraries using given package as a dependency using dumped JSON file
    """
    packages = {'require': [], 'require-dev': [], 'suggest': []}
    
    current = 0
    total = len(libraries)

    for library in libraries:
        current += 1
        sys.stdout.write("\r> parsing dependency %d out of %s libraries...\r" % (current, total))
        sys.stdout.flush()
        
        library_name = library['name']

        for version in library['versions']:
            for type in ['require', 'require-dev', 'suggest']:
                for item in version['packages'][type]:
                    if item == package and library_name not in packages[type]:
                        packages[type].append(library_name)

    return packages

def main(argv):
    """
    Script usage: ./packagist.py [--fetch|--package <package-name>]
    """

    usage = 'usage: ./%s [--fetch|--package <package-name>]' % os.path.basename(__file__)

    try:
        opts, args = getopt.getopt(argv, 'f:p', ['fetch', 'package='])
    except getopt.GetoptError:
        print usage
        sys.exit(2)

    if len(opts) == 0:
        print usage
        sys.exit(2)

    for opt, arg in opts:
        if opt in ['-f', '--fetch']:
            print '> start fetching...'
            packages = fetch_packages()

            with open('packages.json', 'w') as file:
                json.dump(packages, file)

                print 'Packages dependencies has been dumped into packages.json file.'
        elif opt in ['-p', '--package']:
            print '> start parsing, please wait...'
            
            try:
                file = open('packages.json')
            except IOError:
                print '[error] no packages.json file found, you should run: ./%s --fetch' % os.path.basename(__file__)
                sys.exit(2)

            data = json.load(file)
            packages = get_package_dependencies(data, arg)
            
            print "\r"
            print json.dumps(packages, sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == '__main__':
    main(sys.argv[1:])