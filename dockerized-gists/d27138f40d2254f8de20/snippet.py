#!/usr/bin/env python
'''
Analyze Apache log file to identify malicious request sources
'''
from os import path
import sys
import urllib
import json

def apache2_logrow(s):
    ''' Fast split on Apache2 log lines
    http://stackoverflow.com/questions/12544510/parsing-apache-log-files
    '''
    row = [ ]
    qe = qp = None # quote end character (qe) and quote parts (qp)
    for s in s.replace('\r','').replace('\n','').split(' '):
        if qp:
            qp.append(s)
        elif '' == s: # blanks
            row.append('')
        elif '"' == s[0]: # begin " quote "
            qp = [ s ]
            qe = '"'
        elif '[' == s[0]: # begin [ quote ]
            qp = [ s ]
            qe = ']'
        else:
            row.append(s)

        l = len(s)
        if l and qe == s[-1]: # end quote
            if l == 1 or s[-2] != '\\': # don't end on escaped quotes
                row.append(' '.join(qp)[1:-1].replace('\\'+qe, qe))
                qp = qe = None
    return row

def cymon_lookup(ip):
    # lookup IP addresses in Cymon
    url = "https://cymon.io/api/nexus/v1/ip/" + ip  + "/?format=json"
    response = urllib.urlopen(url)
    if response.code == 200:
        return json.loads(response.read())
    return None

def main(log_file):
    # read log file
    lines = open(path.abspath(log_file)).readlines()

    # parse log file
    logs = [ apache2_logrow(line) for line in lines ]

    # create dict with unique IPs
    sources = {}
    for row in logs:
        if len(row) > 3:
            if sources.has_key(row[0]):
                sources[row[0]]['urls'].append(row[4])
            else:
                sources[row[0]] = {'urls': [ row[4] ]}

    # lookup IPs in Cymon (this may be slow, if log file is big)
    for ip in sources.keys():
        res = cymon_lookup(ip)
        if res:
            # add results from cymon
            sources[ip]['cymon'] = res
        else:
            # remove IP with no results
            sources.pop(ip)

    # print results
    if sources:
        print "Log Analysis Results:"
        for ip in sources.keys():
            print "\n[*] IP: %s" %(ip)
            print "[*] Sources: %s" %(", ".join(sources[ip]['cymon']['sources']))
            print "[*] URLs:"
            for url in sources[ip]['urls']:
                print "\t" + url
    else:
        print "No results in Cymon"

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print "Usage: %s <log_file>" %(sys.argv[0])
