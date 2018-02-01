#!/usr/bin/env python

"""
Download all the pdfs linked on a given webpage

Usage -

    python grab_pdfs.py url <path/to/directory>
        url is required
        path is optional. Path needs to be absolute
        will save in the current directory if no path is given
        will save in the current directory if given path does not exist

Requires - requests >= 1.0.4
           beautifulsoup >= 4.0.0

Download and install using
    
    pip install requests
    pip install beautifulsoup4
"""

__author__= 'elssar <elssar@altrawcode.com>'
__license__= 'MIT'
__version__= '1.0.0'

from requests import get
from urlparse import urljoin
from os import path, getcwd
from bs4 import BeautifulSoup as soup
from sys import argv

def get_page(base_url):
    req= get(base_url)
    if req.status_code==200:
        return req.text
    raise Exception('Error {0}'.format(req.status_code))

def get_all_links(html):
    bs= soup(html)
    links= bs.findAll('a')
    return links

def get_pdf(base_url, base_dir):
    html= get_page()
    links= get_all_links(html)
    if len(links)==0:
        raise Exception('No links found on the webpage')
    n_pdfs= 0
    for link in links:
        if link['href'][-4:]=='.pdf':
            n_pdfs+= 1
            content= get(urljoin(base_url, link['href']))
            if content.status==200 and content.headers['content-type']=='application/pdf':
                with open(path.join(base_dir, link.text+'.pdf'), 'wb') as pdf:
                    pdf.write(content.content)
    if n_pdfs==0:
        raise Exception('No pdfs found on the page')
    print "{0} pdfs downloaded and saved in {1}".format(n_pdfs, base_dir)

if __name__=='__main__':
    if len(argv) not in (2, 3):
        print 'Error! Invalid arguments'
        print __doc__
        exit(-1)
    arg= ''
    url= argv[1]
    if len(argv)==3:
        arg= argv[2]
    base_dir= [getcwd(), arg][path.isdir(arg)]
    try:
        get_pdf(base_dir)
    except Exception, e:
        print e
        exit(-1)