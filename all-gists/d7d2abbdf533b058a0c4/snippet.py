#!/usr/bin/env python
# -*- coding: utf-8 -*-
# run this in the directory ~/.config/quassel-irc.org/

import sqlite3
import time

con = sqlite3.connect('quassel-storage.sqlite')

with con:
        senders = {}

        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute('SELECT messageid,senderid,time FROM backlog')
        expire_time = time.time() - (30 * 24 * 60 * 60) # expire before 30 days ago
        deletes = []
        while True:
                row = cur.fetchone()
                if row == None:
                        break
                if row["time"] < expire_time:
                        deletes.append( [ row["messageid"] ] )
                else:
                        id = row["senderid"]
                        if senders.has_key(id):
                                senders[id] += 1
                        else:
                                senders[id] = 1
        cur.executemany("delete from backlog where messageid = ?", deletes)
        print "deleted %d from backlog" % len(deletes)

        cur.execute('SELECT senderid from sender')
        deletes = []
        while True:
                row = cur.fetchone()
                if row == None:
                        break
                if not senders.has_key(row["senderid"]):
                        deletes.append( [ row["senderid"] ] )

        cur.executemany("delete from sender where senderid = ?", deletes)
        print "deleted %d from sender" % len(deletes)

        cur.execute("vacuum")
