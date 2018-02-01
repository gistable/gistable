#!/usr/bin/python
# Delete images from Thumbor cache.
#

import sys
import os
import os.path
from thumbor.storages.file_storage import Storage
from thumbor.context import Context
from thumbor.console import get_server_parameters
from thumbor.config import Config
from urllib import quote

def flush(url):
    print url
    cachefile = storage.path_on_filesystem(quote(url))

    print "\t" + cachefile

    if os.path.isfile(cachefile):
        os.unlink(cachefile)
        print "\tRemoved"
    else: 
        print "\tNot in cache"


if (len(sys.argv) != 2):
    print 'Usage: ' + sys.argv[0] + ' url/file'
    exit(1)

server_parameters = get_server_parameters()
lookup_paths = ['/etc/']
config = Config.load(server_parameters.config_path, conf_name='thumbor.conf', lookup_paths=lookup_paths)
importer = None

context = Context(
    server=server_parameters,
    config=config,
    importer=importer
)

storage = Storage(context)

if os.path.exists(sys.argv[1]):
    with open(sys.argv[1]) as f:
        for url in f:
            flush(url.rstrip())

else:
    flush(sys.argv[1])

print 'All cache files removed'
