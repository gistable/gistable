#!/usr/bin/env python
# urlUniq.py takes a list of URLs and uniqs them.
# If the file contains both http and https, it dumps all duplicate https
# this is useful for creating list-based vuln scans in dire times

import re

#************************************

# Definitions

# This controls results per parameter
RESULTS_PER_PARAM = 10

# This controls how many directories out the script will look before attempting parameter reduction
# NOTE this is post-dedup
# Example: each slash counts as 1 but later logic will account for the inital slashes
# Change START_DIR to match the drectory you wish to start parameter/path reduction
# http://domain/subdir1[1]/subdir2[2]

START_DIR = 2

# List of URLs to trim
INFILE = ''

# Output
OUTFILE = ''

#************************************

def generateInitialLists(file):
    httpURLs= []
    httpsURLs = []
    fs = open(file,'rU')
    i = 1
    for url in fs:
        i = i + 1
        url = url.strip('\n')
        url = url.strip('/')
        redundantPathsRemoved = []
        paths = url.split('/')[2:]

        if len(paths) != len(list(set(paths))):
            #print 'Contains dupes: ' + url
            pass
        elif '?' in ''.join(paths):

            for elem in paths:
                paths[paths.index(elem)] = re.sub('\?.*','',elem)

            if len(paths) != len(list(set(paths))):
                #print 'Contains dupes: ' + url
                pass
            else:
                if 'http://' in url:
                    httpURLs.append(url)
                else:
                    httpsURLs.append(url)
        else:
            if 'http://' in url:
                httpURLs.append(url)
            else:
                httpsURLs.append(url)

    httpURLs = list(set(httpURLs))
    httpsURLs = list(set(httpsURLs))

    searchBuffer = ''.join(httpURLs)

    uncommonURLs = []

    for url in httpsURLs:
        searchPath = '/'.join(url.split('/')[3:])
        searchPath = re.escape(searchPath)
        regex=re.compile(searchPath)
        if regex.search(searchBuffer) is None:
            uncommonURLs.append(url)

    uniqURLs = sorted(httpURLs) + sorted(uncommonURLs)

    print 'What was',i,'is now',len(uniqURLs)
    return uniqURLs

def removeRedundantCalls(initialURLs,RESULTS_PER_PARAM,START_DIR):
    finalList = []
    # Addition to start dir to account for slashes
    # for http(s):// and domain trailing slash
    START_DIR = START_DIR + 2
    for url in initialURLs:
        paths = url.split('/')
        # The length is compared to +1 due to indexing
        if len(paths) >= START_DIR + 1:
            if '?' in paths[-1]:
                frag = url.split('?')[0]
                print frag
            else:
                frag = '/'.join(paths[0:-1])
                print frag

            regex = re.escape(frag)
            regex = re.compile(regex + '\S*')
            matches = regex.findall(' '.join(initialURLs))
            if len(matches) >= RESULTS_PER_PARAM:
                finalList.extend(matches[0:RESULTS_PER_PARAM])
                for match in matches:
                    initialURLs.remove(match)
            elif len(matches) > 0:
                finalList.extend(matches)
                for match in matches:
                    initialURLs.remove(match)
            else:
                finalList.append(url)
                initialURLs.remove(url)
        else:
            finalList.append(url)
            initialURLs.remove(url)
    return finalList

def main():
    file = INFILE
    outfile = open(OUTFILE,'w')
    initialURLs = generateInitialLists(file)
    finalList = removeRedundantCalls(initialURLs,RESULTS_PER_PARAM,START_DIR)
    print 'And finally',len(finalList)
    for url in finalList:
        outfile.write(url+'\n')
    outfile.close()

if __name__ == '__main__':
    main()