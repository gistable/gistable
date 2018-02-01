#!/usr/bin/python2
"""
This script automates the task of connecting to a running App Engine server, 
whether it's a local dev_appserver or a live app.

If PyQt4 is installed, it will ask for credentials inside a dialog box 
instead of prompting in the terminal. This is good for shells that do 
not support getpass (iPython).

It will automatically add an import path for a local virtualenv in the app 
folder path if you're using one (you *are* using virtualenv, right?)

For added fun, you can import your Models in the section below so that they're 
ready to use in the interactive session.

Usage: Either execute this script directly, or import it from within an 
instance of your favorite Python shell.

Configuration options:

- APP_ID: Your app's application ID. Leave this set to None to auto-detect.
- APP_PATH: Path to your app's working directory (where you should have your 
    app.yaml).
- REMOTE_API_PATH: Path to your app's remote_api endpoint. This has to be 
    enabled_ first.
- SAVE_COOKIES: Set to True to save authentication credentials to a file in 
    your $HOME dir.
- SDK_PATH: Path where you extracted the App Engine SDK.
- SECURE: Use https[#]_ for the remote_api connection. 
- SERVER: The server to connect to.

Pro tip: Use this with iPython_ by adding this script to your profile's 
startup directory! 

.. [#]: The dev_appserver does not support https.

.. _iPython: http://ipython.org/ipython-doc/stable/config/overview.html#profiles
.. _enabled: https://developers.google.com/appengine/docs/python/tools/remoteapi

"""

# Main configuration options.
APP_ID = None
APP_PATH = '~/my_app'
REMOTE_API_PATH = '/_ah/remote_api'
SAVE_COOKIES = True
SDK_PATH = '/usr/local/google_appengine'
SECURE = True
SERVER = 'my-app.appspot.com'


print """
Connecting to remote_api server: {}

Starting up...""".format(SERVER)


# Prepare the virtual environment.
import os
import site
import sys
virtual_env = os.path.join(APP_PATH, 'lib', 'python{}.{}'.format(
                           sys.version_info[0], sys.version_info[1]),
                           'site-packages')
site.addsitedir(virtual_env)
os.chdir(APP_PATH)
print 'Virtual environment path: ', virtual_env
del virtual_env, site


print 'Loading App Engine SDK...'
sys.path.insert(0, SDK_PATH)
import dev_appserver
dev_appserver.fix_sys_path()
from google.appengine.ext.remote_api import remote_api_stub
from google.appengine.tools import appengine_rpc
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import ndb
if '' not in sys.path:
    sys.path.insert(0, '')

try:
    from PyQt4 import QtGui

    class LoginDialog(QtGui.QDialog):
        """A simple login dialog with email and password entry."""
        def __init__(self):
            QtGui.QDialog.__init__(self)
            self.setWindowTitle('App Engine remote_api: Login')
            self.email = QtGui.QLineEdit(self)
            self.email.setPlaceholderText('email')
            self.password = QtGui.QLineEdit(self)
            self.password.setEchoMode(QtGui.QLineEdit.Password)
            self.password.setPlaceholderText('password')
            self.button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                                     QtGui.QDialogButtonBox.Cancel)
            self.button_box.accepted.connect(self.handle_login)
            self.button_box.rejected.connect(self.handle_cancel)
            layout = QtGui.QVBoxLayout(self)
            layout.addWidget(self.email)
            layout.addWidget(self.password)
            layout.addWidget(self.button_box)

        def handle_cancel(self):
            self.reject()

        def handle_login(self):
            self.accept()


    def auth_callback():
        app = QtGui.QApplication(sys.argv)
        dialog = LoginDialog()
        if dialog.exec_() == QtGui.QDialog.Accepted:
            del app
            return (str(dialog.email.text()), str(dialog.password.text()))
        else:
            sys.exit(1)
except ImportError:
    from getpass import getpass
    def auth_callback():
        """A fallback for systems that do not have PyQt4 installed."""
        return(raw_input('Email: '), getpass('Password: '))


# Connect to the remote_api endpoint and set up all the service stubs.
remote_api_stub.ConfigureRemoteApi(
    APP_ID,
    REMOTE_API_PATH,
    auth_callback,
    servername=SERVER,
    save_cookies=SAVE_COOKIES,
    secure=SECURE,
    rpc_server_factory=appengine_rpc.HttpRpcServer)
print 'Authenticating...'
remote_api_stub.MaybeInvokeAuthentication()
os.environ['SERVER_SOFTWARE'] = 'Development (remote_api_shell)/1.0'
if APP_ID is None:
    APP_ID = os.environ['APPLICATION_ID']


print 'Loading user imports...'
################################################################################
# Put user imports here, but don't forget to add them to the PREIMPORTED_LOCALS 
# dict below!
#
# Example:
#
# from models import AddressBook
# from models import Car
# from models import Person
#
# PREIMPORTED_LOCALS = {
#     'memcache': memcache,
#     'urlfetch': urlfetch,
#     'users': users,
#     'db': db,
#     'ndb': ndb,
#     'AddressBook': AddressBook,
#     'Car': Car,
#     'Person': Person}

PREIMPORTED_LOCALS = {
    'memcache': memcache,
    'urlfetch': urlfetch,
    'users': users,
    'db': db,
    'ndb': ndb}

################################################################################

# Tweak this to customize the banner message after successful login.
BANNER = """
App Engine remote_api Shell
Python {}
Connected to: {} ({})
Imported modules: {}
""".format(sys.version, APP_ID, SERVER,
           ', '.join(sorted(PREIMPORTED_LOCALS.keys())))


if __name__ == '__main__':
    # Create an interactive shell.
    import atexit
    import code
    try:
        import readline
    except ImportError:
        readline = None
        
    HISTORY_PATH = os.path.expanduser('~/.remote_api_shell_history')
    sys.ps1 = '{}> '.format(APP_ID)
    if readline is not None:
        readline.parse_and_bind('tab: complete')
        atexit.register(lambda: readline.write_history_file(HISTORY_PATH))
    if os.path.exists(HISTORY_PATH):
        readline.read_history_file(HISTORY_PATH)


    if '' not in sys.path:
        sys.path.insert(0, '')

    code.interact(banner=BANNER, local=PREIMPORTED_LOCALS)
else:
    print BANNER
