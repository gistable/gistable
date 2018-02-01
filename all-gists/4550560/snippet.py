#! /usr/bin/env python
from boto.ses.connection import SESConnection
import os
import sys
import subprocess
import socket

TMPFILE = '/var/run/postgresql/last-wal-archive-error-file.tmp'

if __name__ == '__main__':
    return_code = 'unknown'
    host = socket.getfqdn()
    wal_file = 'unknown'
    try:
        ses_conn = SESConnection()
        wal_file = sys.argv[1]
        wal_push = '/usr/local/bin/wal-e'
        return_code = subprocess.call([wal_push, 'wal-push', wal_file])
    except Exception, e:
        return_code = str(e)
    finally:
        if return_code != 0:
            if os.path.exists(TMPFILE):
                contents = open(TMPFILE).read()
                last_wal_error = contents
                if wal_file == last_wal_error:
                    ses_conn.send_email(
                        source = 'youremail@',
                        subject = 'PG WAL Archive Failed!',
                        body = 'Host: %s\nError: %s\nWAL: %s' % (host, return_code, wal_file),
                        to_addresses = ['toemail@'])
                    sys.exit(1)
            outfl = open(TMPFILE, 'w')
            outfl.write(wal_file)
            outfl.close()
            sys.exit(1)
        else:
            if os.path.exists(TMPFILE):
                os.remove(TMPFILE)
            sys.exit(0)