#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script made by Noel B. A. http://www.nbalonso.com

Downloads malware signatures and scans the system for infections.
Built as a module for munkireport-php https://github.com/munkireport
"""

__author__ = 'Noel Barrachina'
__version__ = '0.1'

import sys
import os
import urllib2
from xml.dom import minidom

#Global
cachedir = '%s/cache' % os.path.dirname(os.path.realpath(__file__))

#Define highlight colors
class bcolors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

def manual_check():
    #Skip manual check
    if len(sys.argv) > 1:
        if sys.argv[1] == 'manualcheck':
            return 1

def cache_dir():
    #Create cache dir if it does not exist
    if not os.path.exists(cachedir):
        os.makedirs(cachedir)

def update_signatures():
    signatures = open('%s/signatures.xml' % cachedir, 'w+')
    signatures.write(urllib2.urlopen('http://www.company.com/signatures.xml').read())
    signatures.close()

def version_check():
    #Retrieve the malware definitions version from the website
    try:
         onlineversion = urllib2.urlopen('http://www.companya.com/sigversion.txt').read()
     except:
         return

    #if we know the latest version, compare it against the local one
    if onlineversion:
        try:
            signatures = open('%s/signatures.xml' % cachedir, 'r')
            xmldoc = minidom.parse('%s/signatures.xml' % cachedir)
            localversion = xmldoc.getElementsByTagName('admedicsigs')[0].attributes['version'].value
            signatures.close()
        except:
            #if we have failed to read the local file, needs to be updated
            localversion = 0
        if int(onlineversion) > int(localversion):
            update_signatures()

def load_signatures():
    if os.path.isfile('%s/signatures.xml' % cachedir):
        return open('%s/signatures.xml' % cachedir, 'r')
    else:
        return 0

def malware_scan(signatures):
    results = []
    #Actual parsing
    xmldoc = minidom.parse(signatures)
    adwarelist = xmldoc.getElementsByTagName('adware')

    for adware in adwarelist:
        #to do: malwarename to be used later in the report
        # malwarename = adware.attributes['name'].value

        itemlist = adware.getElementsByTagName('item')
        for item in itemlist:
            type = item.attributes['type'].value
            #Switch for the four types of detection
            #1
            if type == 'path':
                path = item.childNodes[0].nodeValue
                #check if path is relative
                try:
                    relative = item.attributes['relativeTo'].value
                except:
                    #no value is considered full path
                    relative = 'no'
                #check if the file can be legit
                try:
                    optional = item.attributes['optional'].value
                except:
                    #no value will trigger infection if found
                    optional = 'false'
                infected = scan_path(path,relative,optional)
                if infected:
                    results.append(infected)

            #These 3 types are still to investigate
            #2
            elif type == 'extName':
                regex = item.childNodes[0].nodeValue
                infected = scan_extname(regex)
                if infected:
                    results.append(infected)
            #3
            elif type == 'login':
                scan_login()
            #4
            elif type == 'extContent':
                scan_extcontent()

    return results

def scan_path(path,isrelative,isoptional):
    #1 paths relative to home
    if isrelative == 'home':
        homes = os.listdir('/Users')
        for home in homes:
            #ignore dot folders and Shared
            if (not home.startswith('.')) and (home != 'Shared'):
                fullpath = '/Users/' + home + '/'+ path
                #to do: optional files never report as infected. grep 'em or something
                if os.path.exists(fullpath) and not isoptional:
                    #Infection here!
                    return(fullpath)
    #2 ffox profile paths
    elif isrelative == 'ffprofile':
        homes = os.listdir('/Users')
        for home in homes:
            #ignore dot folders and Shared
            if (not home.startswith('.')) and (home != 'Shared'):
                #list the ffox profiles
                try:
                    ffoxprofiles = os.listdir('/Users/' + home + \
                        '/Library/Application Support/Firefox/Profiles')
                    for ffoxprofile in ffoxprofiles:
                        #ignore dot folders
                        if not ffoxprofile.startswith('.'):
                            fullpath = '/Users/' + home + \
                                '/Library/Application Support/Firefox/Profiles/' \
                                + ffoxprofile + '/' + path
                            if os.path.exists(fullpath) and not isoptional:
                                #Infection!
                                return(fullpath)
                #if there is no ffox profiles path to open, just skip
                except:
                    pass
    #3 Absolute paths
    else:
        if os.path.exists(path) and not isoptional:
            #Infection
            return(fullpath)

def scan_extname(regex):
    homes = os.listdir('/Users')
    for home in homes:
        #ignore dot folders and Shared
        if (not home.startswith('.')) and (home != 'Shared'):
            extspath = '/Users/' + home + '/Library/Safari/Extensions/'
            #to do: we need to do a split for each | and remove (), then loop with find subprocess
            if os.path.exists(extspath):
                print regex

    return

def scan_login():
    return

def scan_extcontent():
    return

def main():
    print 'Malware Detector (version %s)' % __version__
    print ''
    if manual_check():
        print 'Manual check: skipping'
        sys.exit(0)
    cache_dir()
    version_check()
    signatures = load_signatures()
    if not signatures:
        print bcolors.YELLOW + 'Cannot load definitions. Exiting' + bcolors.ENDC
        sys.exit(0)
    mal_files = malware_scan(signatures)
    if len(mal_files) != 0:
        for file in mal_files:
            print bcolors.RED + 'Suspicious file at: %s' % file + bcolors.ENDC
    else:
        print bcolors.GREEN + 'No malware was found' + bcolors.ENDC


    #final exit
    sys.exit(0)

if __name__ == '__main__':
    main()
