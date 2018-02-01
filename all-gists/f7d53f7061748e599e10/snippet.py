#!/usr/bin/python

##########################################
## Downloads bibtex file from Citeulike.
## By: Andy Shi
## For help and usage, execute
##  python download_citations.py -h
## Inspired by:
## http://linuxtoosx.blogspot.com/2012/10/downloadbackup-citeulike-library.html
##########################################

import argparse
import requests

# set your Citeulike username and password here
USERNAME = "USERNAME"
PASSWORD = "PASSWORD"

# argparse configuration
DEFAULT_OUTPUT = "export.bib"
DESCRIPTION = "Download bibtex citation file from citeulike."

# process command line arguments
def handle_cli():
    parser = argparse.ArgumentParser(description = DESCRIPTION)
    parser.add_argument("-o", "--output", default = DEFAULT_OUTPUT,
            help = "Bibtex output file name. Default: " + DEFAULT_OUTPUT)
    parser.add_argument("-t", "--tag",
            help = "Which tag to use. By default, no tags are used.")
    args = parser.parse_args()
    return(args)

def main():
    args = handle_cli()
    with requests.Session() as s:
        # log in to citeulike
        payload = {'username': USERNAME, 'password': PASSWORD, 'perm': 1}
        r_login = s.post("http://www.citeulike.org/login.do", data=payload)

        if args.tag:
            # download citations with a certain tag
            url = \
            "http://www.citeulike.org/bibtex/user/{}/tag/{}".format(USERNAME,
                    args.tag)
        else:
            # download all citations
            url = "http://www.citeulike.org/bibtex/user/{}".format(USERNAME)
        r_bibtex = s.get(url)

        # write bibtex to file
        chunk_size = 1024
        with open(args.output, 'wb') as fd:
            for chunk in r_bibtex.iter_content(chunk_size):
                fd.write(chunk)

if __name__ == "__main__":
    main()
    

#########################################
# LICENSE
# The MIT License (MIT)

# Copyright (c) 2016 Andy Shi

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#########################################
