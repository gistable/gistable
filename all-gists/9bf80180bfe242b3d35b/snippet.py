#!/usr/bin/env python3

import sqlite3
import sys
import subprocess
from urllib.parse import quote


def main():
    if len(sys.argv) < 2:
        print("Not enough arguments!", file=sys.stderr)
        exit(1)

    try:
        record_id = -1
        if len(sys.argv) >= 3:
            try:
                record_id = int(sys.argv[2])
            except ValueError:
                print("Ignoring invalid record number", file=sys.stderr)
        conn = sqlite3.connect(sys.argv[1])
        c = conn.cursor()
        if record_id != -1:
            sql = 'select * from accounts where _id == ' + str(record_id)
            c.execute(sql)
            row = c.fetchone()
            if not row:
                print("No such record", file=sys.stderr)
                exit(1)
            (_, email, secret, counter, type, _, issuer, _) = row
            url = 'otpauth://'
            url += 'totp' if type == 0 else 'hotp'
            url += '/' + quote(email) + '?secret=' + quote(secret)
            url += '&issuer=' + quote(issuer) if issuer else ''
            url += '&counter=' + str(counter) if type == 1 else ''
            print(url)
            subprocess.call(['qrencode', '-tUTF8', url])
        else:
            sql = 'select _id, email, issuer from accounts'
            for id, email, issuer in c.execute(sql):
                if issuer is None:
                    issuer = 'Unknown'
                print("%d: %s %s" % (id, issuer, email))
            print("Which do you want to restore?")
    except IOError as e:
        print("Error opening file!", e.strerror(), file=sys.stderr)


if __name__ == '__main__':
    main()
