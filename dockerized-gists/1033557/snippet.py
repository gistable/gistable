#!/usr/bin/env python

import sys

import couchdb

if __name__ == '__main__':

    srcurl, desturl = sys.argv[1:]

    print "from", srcurl, "to", desturl

    src = couchdb.Server(srcurl)
    dest = couchdb.Server(desturl)

    todo = [db for db in src if db[0] != '_']

    destrep = dest['_replicator']
    docs = []

    for db in todo:
        print "Doing", db
        if db not in dest:
            print "Creating..."
            dest.create(db)

        rk = "clone-" + db
        doc = {'_id': rk, 'source': srcurl + db, 'target': db, 'continuous': True,
               'user_ctx': { 'roles': [ "_admin" ] }
               }

        docs.append(doc)

    destrep.update(docs)
