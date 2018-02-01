#!/usr/bin/env python
# coding: utf-8

#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""An interactive python shell that uses remote_api.

Usage:
  %prog [-s HOSTNAME] [-p PATH] [--secure] [APPID]

If the -s HOSTNAME flag is not specified, the APPID must be specified.

Use "-s localhost:8080" for local dev server connection
"""

import os
import sys
import atexit
import code
import getpass
import optparse
from functools import partial

try:
    import readline
except ImportError:
    readline = None

try:
    from IPython.terminal.console.interactiveshell import (
        TerminalInteractiveShell, )
except ImportError:
    TerminalInteractiveShell = None

ROOT = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), '..'
)


def rel(path):
    return os.path.join(ROOT, path)


sys.path.insert(0, ROOT)

APP_ENGINE_SDK = os.environ.get('APP_ENGINE_SDK_PATH', '../google_appengine')
sys.path.insert(1, rel(APP_ENGINE_SDK))
try:
    import dev_appserver
except:
    dev_appserver = None
    raise EnvironmentError("Can not find dev_appserver inside python paths")

dev_appserver.fix_sys_path()


from google.appengine.ext.remote_api import remote_api_stub
from google.appengine.tools import appengine_rpc
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import ndb


HISTORY_PATH = os.path.expanduser('~/.remote_api_shell_history')
DEFAULT_PATH = '/_ah/remote_api'
BANNER = """App Engine remote_api shell
Python %s
The db, ndb, users, urlfetch, and memcache modules are imported.\
""" % sys.version


def auth_func(email=None, password=None):
    email = email or raw_input('Email: ')
    password = password or getpass.getpass('Password: ')
    return email, password


def remote_api_shell(servername, appid, path, secure, rpc_server_factory,
                     email=None, password=None,
                     ipython=True):
    """Actually run the remote_api_shell."""
    auth = partial(auth_func, email=email, password=password)
    remote_api_stub.ConfigureRemoteApi(appid, path, auth,
                                       servername=servername,
                                       save_cookies=True, secure=secure,
                                       rpc_server_factory=rpc_server_factory)
    remote_api_stub.MaybeInvokeAuthentication()


    os.environ['SERVER_SOFTWARE'] = 'Development (remote_api_shell)/1.0'

    if not appid:
        appid = os.environ['APPLICATION_ID']
    sys.ps1 = '%s> ' % appid
    if readline is not None:

        readline.parse_and_bind('tab: complete')
        atexit.register(lambda: readline.write_history_file(HISTORY_PATH))
        if os.path.exists(HISTORY_PATH):
            readline.read_history_file(HISTORY_PATH)


    if '' not in sys.path:
        sys.path.insert(0, '')

    preimported_locals = {
        'memcache': memcache,
        'urlfetch': urlfetch,
        'users': users,
        'db': db,
        'ndb': ndb,
        }

    if ipython and TerminalInteractiveShell:
        ishell = TerminalInteractiveShell(banner1=BANNER,
                                          user_ns=preimported_locals)
        ishell.mainloop()
    else:
        code.interact(banner=BANNER, local=preimported_locals)


def main(argv):
    """Parse arguments and run shell."""
    parser = optparse.OptionParser(
        usage=__doc__
    )
    parser.add_option('-s', '--server', dest='server',
                      help='The hostname your app is deployed on. '
                           'Defaults to <app_id>.appspot.com.')
    parser.add_option('-p', '--path', dest='path',
                      help='The path on the server to the remote_api handler. '
                           'Defaults to %s.' % DEFAULT_PATH)
    parser.add_option('--secure', dest='secure', action="store_true",
                      default=False, help='Use HTTPS when communicating '
                                          'with the server.')
    parser.add_option('-I', '--ipython', default=True,
                      help='set ipython as default shell interpreter')
    parser.add_option('-e', '--email', dest='email',
                      help='authentication email', default=False)
    parser.add_option('-P', '--password', dest='password',
                      help='authentication password (password is given '
                           'in plain type, so do not provide to avoid any '
                           'security risk if you do not sure what you are '
                           'doing', default=False)
    (options, args) = parser.parse_args()

    if ((not options.server and not args) or len(args) > 2
        or (options.path and len(args) > 1)):
        parser.print_usage(sys.stderr)
        if len(args) > 2:
            print >> sys.stderr, 'Unexpected arguments: %s' % args[2:]
        elif options.path and len(args) > 1:
            print >> sys.stderr, 'Path specified twice.'
        sys.exit(1)


    servername = options.server
    appid = None
    email = options.email
    password = options.password

    path = options.path or DEFAULT_PATH
    if args:
        if servername:

            appid = args[0]
        else:

            servername = '%s.appspot.com' % args[0]
        if len(args) == 2:

            path = args[1]
    remote_api_shell(servername, appid, path, options.secure,
                     appengine_rpc.HttpRpcServer,
                     email=email, password=password)


if __name__ == '__main__':
    main(sys.argv)
