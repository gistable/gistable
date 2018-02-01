#!/usr/bin/env python2.7

import argparse
import os
import qrcode
import qrcode.image.pil
import sqlite3
import sys
import urllib

class AuthenticatorAccount(object):

    def __init__(self, account_name, account_desc, secret):
        self.account_name = account_name
        self.account_desc = account_desc
        self.secret = secret

    def __repr__(self):
        return "AuthenticatorAccount@%s%s" % (hex(id(self))[2:], self.__dict__)

def __main__():
    parser = argparse.ArgumentParser()
    parser.add_argument("database", help="The SQLite database file.")
    args = parser.parse_args()

    if not os.path.isfile(args.database):
        sys.stderr.write("Unable to open %s.\n" % (args.database,))
        sys.stderr.flush()
        sys.exit(1)

    conn = sqlite3.connect(args.database)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounts ORDER BY _id;")
    
    row = None

    while True:
        row = cursor.fetchone()

        if row is None:
            break

        account = AuthenticatorAccount(row['issuer'] or row['original_name'], row['email'],
                row['secret'])
    
        print """Saving "%s" to "qrcode-account-%02d.svg" """[:-1] % (account.account_desc,
                row['_id'])
        
        qr = qrcode.make("otpauth://totp/%s?secret=%s&issuer=%s" % (account.account_desc,
            account.secret, account.account_name), image_factory=qrcode.image.pil.PilImage)
        
        with open("qrcode-account-%02d.png" % (row['_id'],), "wb") as f:
            qr.save(f)


if __name__ == "__main__":
    __main__()
