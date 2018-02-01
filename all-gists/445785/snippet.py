#!/usr/bin/env python
# coding: utf-8

from gevent import monkey; monkey.patch_all()
from gevent.wsgi import WSGIServer

import os
import logging
log = logging.getLogger(__name__)

from paste.deploy import loadapp


PORT = 8088

def main():
    config_path = os.path.join(os.path.abspath(os.path.curdir), 'development.ini')
    wsgi_app = loadapp('config:' + config_path)
    log.info('Serving on %d...' % PORT)
    WSGIServer(('', PORT), wsgi_app).serve_forever()

if __name__ == '__main__':
    main()