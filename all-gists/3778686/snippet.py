#!/usr/bin/env python
import sys
import Globals
from transaction import commit
from Products.ZenUtils.ZenScriptBase import ZenScriptBase
dmd = ZenScriptBase(connect=True).dmd

if len(sys.argv) < 3:
    print "Usage: %s <source_user> <destination_user>" % (sys.argv[0],)
    sys.exit(1)

sourceUser = getattr(dmd.ZenUsers, sys.argv[1], None)
if not sourceUser:
    print "%s is not a valid user." % (sys.argv[1],)
    sys.exit(2)

destUser = getattr(dmd.ZenUsers, sys.argv[2], None)
if not destUser:
    print "%s is not a valid user." % (sys.argv[2],)
    sys.exit(3)

print "Copying dashboard settings from %s to %s" % (sourceUser.id, destUser.id)
destUser.dashboardState = sourceUser.dashboardState
commit()