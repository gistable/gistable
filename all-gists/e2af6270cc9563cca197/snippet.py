import os

from twisted.application import service
from buildbot.main import BuildMain
from buildsubordinate.bot import BuildSubordinate

# setup main
basedir = os.path.abspath(os.path.dirname(__file__))
configfile = 'main.cfg'

# Default umask for server
umask = None

# note: this line is matched against to check that this is a buildmain
# directory; do not edit it.
application = service.Application('buildmain')
import sys

from twisted.python.log import ILogObserver, FileLogObserver

application.setComponent(ILogObserver, FileLogObserver(sys.stdout).emit)

m = BuildMain(basedir, configfile, umask)
m.setServiceParent(application)

# and subordinate on the same process!

buildmain_host = 'localhost'
port = 19989
subordinatename = 'example-subordinate'
passwd = 'pass'
keepalive = 600
usepty = 0
umask = None
maxdelay = 300
allow_shutdown = None
subordinatedir = os.path.join(basedir, "subordinate")
if not os.path.exists(subordinatedir):
    os.mkdir(subordinatedir)

s = BuildSubordinate(buildmain_host, port, subordinatename, passwd, subordinatedir,
               keepalive, usepty, umask=umask, maxdelay=maxdelay,
               allow_shutdown=allow_shutdown)
s.setServiceParent(application)
