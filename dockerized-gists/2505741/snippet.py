import os

def chgrp(filepath, gid):
    uid = os.stat(filepath).st_uid
    os.chown(filepath, uid, gid)
