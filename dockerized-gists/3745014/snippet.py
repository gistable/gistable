# if you can, just use wget
# wget -np -r remote_url

import re
import os
import urllib2
import urlparse
import pycurl
from lxml import html

url = "http://some.remote.org/"
path = "path/to/dir/listing/"
local = '/path/to/local/parent/directory/'

def walk_directory(remote_path, local_dir):
    response = html.parse(urllib2.urlopen(remote_path))
    links = response.findall('//a')

    link_pattern = '(%s)([^?]+)' % remote_path
    for link in links:
        link.make_links_absolute()
        if not re.match(link_pattern, link.get('href')):
            continue
        filename = re.match(link_pattern, link.get('href')).groups()[-1]
        is_file = not filename.endswith('/')
        if not is_file: # got a directory, recurse
            # make sure this directory exists locally
            if not os.path.exists(os.path.join(local_dir, filename)):
                os.makedirs(os.path.join(local_dir, filename))
            walk_directory(link.get('href'), os.path.join(local_dir, filename))
        else:
            download_file(link.get('href'), os.path.join(local_dir, filename))

def download_file(remote, local):
    with open(local, 'wb') as fout:
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, remote)
        curl.setopt(pycurl.WRITEDATA, fout)
        curl.perform()
        curl.close()

remote_path = urlparse.urljoin(url, path)
if not os.path.exists(local):
    os.makedirs(local)
walk_directory(remote_path, local)