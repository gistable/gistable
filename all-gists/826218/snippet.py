#!/usr/bin/env python
"""
Add php-serve.py to your PATH, then, from whatever directory is the root
of your PHP application, just run:

    $ php-serve.py

You can optionally specify a port number as an argument. By default,
port 8000 is used:

    $ php-serve.py 8000

php-serve.py uses wphp and so has the same restrictions, including no
current support for mod_rewrite. Other than that, it mostly works.

"""
import os
import sys

from paste import httpserver
from wphp import PHPApp


application = PHPApp(os.getcwd())

if len(sys.argv) > 1:
    port = sys.argv[1]
else:
    port = 8000

try:
    httpserver.serve(application, host='0.0.0.0', port=port,
                     daemon_threads=True)
except KeyboardInterrupt:
    application.close()