#!/usr/bin/env python2.7

"""
Copy data from one redis instance to another
"""

import argparse
import sys

# pip install redis fin
import redis
import fin.contextlog


def connect(connection_str):
    parts = connection_str.split(":")
    port = 6379
    db_num = 0
    if len(parts) > 3:
        raise ValueError("Invalid connection string")
    if len(parts) > 2:
        db_num = int(0 if parts[2] == "" else parts[2])
    if len(parts) > 1:
        port = int(6379 if parts[1] == "" else parts[1])
    host = parts[0]
    return redis.Redis(host=host, port=port, db=db_num)


def parse_args(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('db_from', help='Redis server to copy from: host[:port[:db]]')
    parser.add_argument('db_to', help='Redis server to copy to host[:port[:db]]')
    parser.add_argument('--pattern', help='Only copy keys matching pattern', default=None)
    parser.add_argument('-c', "--chunk", help='Chunk size', default=100)

    options = parser.parse_args(args)
    options.error = parser.error
    return options


def main():
    options = parse_args()
    db_from = connect(options.db_from)
    db_to = connect(options.db_to)

    copied = 0
    with fin.contextlog.Log("Copying keys"):
        cur = 0
        while cur != "0":
            cur, keys = db_from.scan(cursor=cur, match=options.pattern, count=options.chunk)
            if len(keys):
                with fin.contextlog.Log("Found Items: %s -> %s" % (copied, copied + len(keys))):
                    pull = db_from.pipeline()
                    for key in keys:
                        pull.dump(key).pttl(key)
                    data = pull.execute()

                    push = db_to.pipeline()
                    for key, data, ttl in zip(keys, data[::2], data[1::2]):
                        if ttl is None:
                            ttl = 0
                        if ttl < -1:
                            print key, ttl
                            continue
                        if ttl < 0:
                            ttl = 0
                        push.restore(key, ttl, data)
                    push.execute()
                    copied += len(keys)
    

if __name__ == "__main__":
    sys.exit(main())
