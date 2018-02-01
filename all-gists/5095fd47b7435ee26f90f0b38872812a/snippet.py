#!/usr/bin/env python
# -*- coding: utf-8 -*-
#######################################################################
# Ksearch provides a simple search interface for the amazing Koodous 
# platform: https://koodous.com/
#
# With Ksearch you have a simple way to integrate Koodous search into
# any of your python projects. This gives you the ability to quickly 
# crowdsource the analysis of potentially malicious Android files.
# 
# You must first register for API access: https://koodous.com/register
#
#
# WARNING! Ksearch uses undocumented APIs that may break at any point!
#
# DOUBLE WARNING!! The Ksearch author is _not_ affiliated with Koodous!!
# 
# TRIPLE WARNING!!! Use at your own risk, responsibility is 100% yours!!! 
#
#######################################################################

__author__ = '@herrcore'
__version__ = 0.3

import json
import urllib
import hashlib
import argparse
import time
import sys
import os
import hashlib
import time

try:
    import requests
except ImportError:
    print "ERROR: You must have the requests installed in your path. For installation see here: http://docs.python-requests.org/en/master/user/install/#install"


#######################################################################
# ** This is really what matters, easy integration of APK crowdsource 
#    malware analysis into all your Python projects with one simple class.
#
#######################################################################
class Ksearch: 
    """
        Class for searching Koodous API.
        WARNING: relies on undocumented APIs
    """

    TOKEN = '!!!!! ADD YOUR TOKEN HERE !!!!!'
    API_URL = 'https://koodous.com/api/%s%s%s'
    PUBLIC_RULE_URL = 'https://analyst.koodous.com/rulesets/'

    def __init__(self, token=None, proxies=None, verify_ssl=None):
        """
            token: Koodous token
            proxies: {<type>: <domain>:<port>} ex. {'https': 'socks5://10.10.1.10:8080'}
            verify_ssl: true/false !!DANGER!! setting this to False will ignore SSL certificate warnings! 
        """
        if token is not None:
            self.TOKEN = token
        
        if proxies is not None:
            self.proxies = proxies
        else:
            self.proxies = {}

        if verify_ssl is not None:
            self.verify_ssl = verify_ssl
        else:
            self.verify_ssl = True


        self.headers = {'Authorization': 'Token %s' % self.TOKEN}


    def get_info(self, sha256):
        """
            Get info for apk
        """
        url = self.API_URL % ('apks/', sha256, '')
        return requests.get(url, headers=self.headers, proxies=self.proxies, verify=self.verify_ssl)


    def search_koodous_db(self, term, page=1, page_size=100):
        """
            Search Koodous APKs for matching term
        """
        url = self.API_URL % ('apks', '?search=%s&page=%i&page_size=%i' % (term, page, page_size), "" )
        return requests.get(url=url, headers=self.headers, proxies=self.proxies, verify=self.verify_ssl)


    def get_detections(self, sha256):
        """
            Function to get detections for APK
            WARNING: relies on undocumented API
        """
        #access undocumented detections API
        url = self.API_URL % ('apks/', sha256, '/detections')
        return requests.get(url=url, headers=self.headers, proxies=self.proxies, verify=self.verify_ssl)


    def get_rule(self, ruleset_id):
        """
            Function to get rule
        """
        #access undocumented rule API
        url = self.API_URL % ('public_rulesets/', ruleset_id, '') 
        return requests.get(url=url, headers=self.headers, proxies=self.proxies, verify=self.verify_ssl)


    def get_rule_yara(self, ruleset_id):
        """
            Function to get rule yara signature
        """
        r = self.get_rule(ruleset_id)
        if r.status_code == 200:
            return r.json().get("rules")
        else:
            return ""


    def get_apk_detections_by_name(self, apk_name):
        """
            Return dictionary of APK hashes that match package name
            and the detections for each hash. 
            [{hash:sha256, detections:[{name,id,link,yara},,,]},,,]
        """
        apk_hashes = []

        r = self.search_koodous_db(apk_name)

        #get sha256 hashes for APKs that have same package name
        #and have been analyzed
        if r.json().get('count') > 0:
            for result in r.json().get('results'):
                if result.get('package_name') == apk_name:
                    if result.get('analyzed') == True:
                        apk_hashes.append(result.get('sha256'))
        
        #get detections for each APK hash
        results =[]
        for apk_hash in apk_hashes:
            detections = self.get_apk_detections_by_hash(apk_hash)
            results.append({"hash":apk_hash, "detections":detections})

        return results


    def get_apk_detections_by_hash(self, sha256):
        """
            Return list of detections and description link. 
            [{name,id,link,yara},,,]
        """
        detections = []

        i = self.get_info(sha256)
        if i.status_code == 200:
            if i.json().get("detected") == True:
                d = self.get_detections(sha256)
                if d.status_code == 200:
                    for detection in d.json():
                        if detection.get("detected") == True:
                            for rule in detection.get("rulesets"):
                                r_name = rule.get("name")
                                r_id = str(rule.get("id"))
                                detections.append({"name":r_name, "id":r_id, "link":self.PUBLIC_RULE_URL+r_id, "yara":self.get_rule_yara(r_id)})
        return detections


#######################################################################
# This is just some fun CLI stuff to demonstrate how Ksearch might 
# be integrated into your projects : ))
#######################################################################

def banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print
    print '####################################################################'
    print '#'
    print '#   _   __                _                   _____ _    _____ '
    print '#  | | / /               | |                 /  __ \ |  |_   _|'
    print '#  | |/ /  ___   ___   __| | ___  _   _ ___  | /  \/ |    | |  '
    print '#  |    \ / _ \ / _ \ / _` |/ _ \| | | / __| | |   | |    | |  '
    print '#  | |\  \ (_) | (_) | (_| | (_) | |_| \__ \ | \__/\ |____| |_ '
    print '#  \_| \_/\___/ \___/ \__,_|\___/ \__,_|___/  \____|_____|___/ '
    print '#'
    print '#       Bringing the magic of Koodous to a CLI near you!'
    print '#'
    print '#                      Version %s' % __version__
    print '#'
    print '####################################################################\n'

def color(text, color_code):
    if sys.platform == "win32" and os.getenv("TERM") != "xterm":
        return text
    return '\x1b[%dm%s\x1b[0m' % (color_code, text)

def red(text):
    return color(text, 31)

def green(text):
    return color(text, 32)

def bold(text):
    if sys.platform == "win32" and os.getenv("TERM") != "xterm":
        return text
    return '\033[1m%s\033[0m' % text

def main():
    parser = argparse.ArgumentParser(description='Search Koodous for crowdsource APK malware detections!')
    subparsers = parser.add_subparsers(help='', dest='subparser_name')
    parser.add_argument('--key',dest="api_key",default=None,help="Specify Koodous API key. Default is the hardcoded TOKEN in ksearch Class.")
    parser.add_argument('-v','--verbose',dest="verbose",default=False,action='store_true',help="Print the Yara signatures responsible for the detections.")
    parser.add_argument('--socks_proxy',dest="socks_proxy",default=None,help="Specify socks proxy <domain>:<port> or <user>:<pass>@<domain>:<port>")
    parser.add_argument('--http_proxy',dest="http_proxy",default=None,help="Specify http proxy <domain>:<port>")
    parser.add_argument('--ignore_ssl',dest="ignore_ssl",default=False,action='store_true',help="DANGER! Ignore SSL certifcate warnings.")

    # create the parser for pkgname
    parser_pkgname = subparsers.add_parser('pkgname', help='Search by APK package name, this needs to be an exact match. Ex. "com.something.something"')
    parser_pkgname.add_argument("pkgname", help="APK package name. Must be an exact match.")
    parser_pkgname.add_argument('--bulk',dest="bulk",default=False,action='store_true',help="Bulk lookup. Pass a file with one package name per line.")

    # create the parser for hash
    parser_hash = subparsers.add_parser('hash', help='Search by APK sha256 hash.')
    parser_hash.add_argument("hash", help="APK sha256 hash.")


    args = parser.parse_args()

    #add in a little flair
    banner()

    #DANGER!! If you ignore SSL errors anyone can snoop on your traffic!
    if args.ignore_ssl == True:
        verify_ssl = False
    else:
        verify_ssl = True


    #obviously we only want to use one type of proxy so
    #socks takes precedent 
    if args.socks_proxy != None:
        print "!!WARNING!! \nSocks is not a default feature in requests! \nMake sure you have installed the additional dependencies or you will get errors. \nSee: http://docs.python-requests.org/en/master/user/advanced/#socks\n\n"
        proxies = {'http':'socks5://' + args.socks_proxy,  'https':'socks5://' + args.socks_proxy}
    elif args.http_proxy != None:
        proxies = {'http':'http://' + args.http_proxy,  'https':'https://' + args.http_proxy}
    else:
        proxies = {}

    #Instantiate ksearch class
    #if no api_key is specified use hard coded TOKEN
    #WARNING! If you have not configured the hard coded TOKEN you must pass an API key!
    if args.api_key != None:
        k = Ksearch(token=args.api_key, proxies=proxies, verify_ssl=verify_ssl)
    else:
        k = Ksearch(proxies=proxies, verify_ssl=verify_ssl)


    #search Koodous by package name or by hash
    if args.subparser_name == "pkgname":
        apk_names = []

        #if this is a bulk lookup add each line in the bulk file as a new pkgname
        if args.bulk:
            with open(args.pkgname) as fp:
                data = fp.readlines()
            for line in data:
                apk_names.append(line.strip())
        else:
            apk_names.append(args.pkgname)

        print "Accessing Koodous API ...\n"
        print "This may take a minute or two ...\n"
        for apk_name in apk_names:
            hashes = k.get_apk_detections_by_name(apk_name)
            print "Results for: %s" % bold(apk_name)
            for app in hashes:
                if len(app['detections']) > 0:
                    print "\t %s" % red(app['hash'])
                else:
                    print "\t %s" % green(app['hash'])
                for detection in app['detections']:
                    print "\t\t\_ %s" % bold(red(detection['name']))
                    print "\t\t\t[-] Link: %s" % detection['link']
                    if args.verbose:
                        print "\t\t\t[-] Yara: \n\t\t\t\t####################################################################################"
                        print "\t\t\t\t#\t %s" % detection['yara'].replace('\n','\n\t\t\t\t#\t')
                        print "\t\t\t\t####################################################################################"


    elif args.subparser_name == "hash":
        apk_hash = args.hash
        print "Accessing Koodous API ...\n"
        print "This may take a minute or two ...\n"
        detections = k.get_apk_detections_by_hash(apk_hash)
        print "Results for: %s" % bold(apk_hash)
        for detection in detections:
                print "\t\t\_ %s" % bold(red(detection['name']))
                print "\t\t\t[-] Link: %s" % detection['link']
                if args.verbose:
                    print "\t\t\t[-] Yara: \n\t\t\t\t####################################################################################"
                    print "\t\t\t\t#\t %s" % detection['yara'].replace('\n','\n\t\t\t\t#\t')
                    print "\t\t\t\t####################################################################################"



if __name__ == '__main__':
    main()