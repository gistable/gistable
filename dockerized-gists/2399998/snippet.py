#!/usr/bin/env python
#-*-coding:utf8-*-
#
# File: gist.py
# Author: Mathieu (matael) Gaborit
#       <mat.gaborit@gmx.com>
# Date: 2012
# License: WTFPL

import os
import sys
import codecs
import json
from urllib2 import urlopen

def main():
    """ Main function """

    # Not enough arguments... or too much
    if len(sys.argv) != 2:
        print("""

> You should specify one (and only one) gist ID

Usage :
    gist.py <gist id>

""")
        exit(0)
    
    # Get id
    id = sys.argv[1]
    print("Assuming {} is a gist ID".format(id))

    # Try to open the URL
    try:
        url = urlopen("https://api.github.com/gists/{}".format(id))
        data = url.read()
        url.close()
    except ValueError:
        print("This URL does not exist... try something else !")
        exit(0)

    # Conversion
    data = json.loads(data)

    # Extraction
    ## Creating directory
    print("Gist ID : {0}\n\tAuthor : {1}".format(
        data['id'],
        data['user']['login']
    ))

    try:
        print("\nMaking directory and entering...\n")
        os.mkdir("gist-{}".format(data['id']))
        os.chdir("gist-{}".format(data['id']))
    except OSError:
        print("Unable to create/go to the right directory\n\tDoes it already exists ?\nGoing to quit...\n")
        exit(0)

    
    number_of_files = len(data['files'].keys())
    print("{} file(s) detected\n".format(number_of_files))
    current_count = 1
    for file in data['files'].keys():
        print("Working on file {0} out of {1} ({2})".format(
            current_count,
            number_of_files,
            file
        ))
        fh = codecs.open(file, 'w', encoding='utf8')
        fh.write(data['files'][file]['content'])
        fh.close()

    ## Forks ?
    if len(data['forks']):
        print("\n\nForks exist :")
        for f in data['forks']:
            print("\n+ gist {0} by {1}\n\thttps://gist.github.com/{0}".format(f['id'], f['user']['login']))
    else:
        print("\n\nNobody forked...")
        
    ## Coming back to previous dir
    print("\nLeaving directory...\n")
    os.chdir('..')

if __name__=='__main__':main()
