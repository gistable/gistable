"""
Copies all keys from the source Redis host to the destination Redis host.
Useful to migrate Redis instances where commands like SLAVEOF and MIGRATE are
restricted (e.g. on Amazon ElastiCache).

The script scans through the keyspace of the given database number and uses
a pipeline of DUMP and RESTORE commands to migrate the keys.

Requires Redis 2.8.0 or higher.

Python requirements:
click==4.0
progressbar==2.3
redis==2.10.3
"""

import click
from progressbar import ProgressBar
from progressbar.widgets import Percentage, Bar, ETA
import redis
from redis.exceptions import ResponseError

@click.command()
@click.argument('srchost')
@click.argument('dsthost')
@click.option('--db', default=0, help='Redis db number, default 0')
@click.option('--flush', default=False, is_flag=True, help='Delete all keys from destination before migrating')
def migrate(srchost, dsthost, db, flush):
    if srchost == dsthost:
        print 'Source and destination must be different.'
        return

    source = redis.Redis(srchost, db=db)
    dest = redis.Redis(dsthost, db=db)

    if flush:
        dest.flushdb()

    size = source.dbsize()

    if size == 0:
        print 'No keys found.'
        return

    progress_widgets = ['%d keys: ' % size, Percentage(), ' ', Bar(), ' ', ETA()]
    pbar = ProgressBar(widgets=progress_widgets, maxval=size).start()

    COUNT = 2000 # scan size

    cnt = 0
    non_existing = 0
    already_existing = 0
    cursor = 0

    while True:
        cursor, keys = source.scan(cursor, count=COUNT)
        pipeline = source.pipeline()
        for key in keys:
            pipeline.pttl(key)
            pipeline.dump(key)
        result = pipeline.execute()

        pipeline = dest.pipeline()

        for key, ttl, data in zip(keys, result[::2], result[1::2]):
            if ttl is None:
                ttl = 0
            if data != None:
                pipeline.restore(key, ttl, data)
            else:
                non_existing += 1

        results = pipeline.execute(False)
        for key, result in zip(keys, results):
            if result != 'OK':
                e = result
                if hasattr(e, 'message') and (e.message == 'BUSYKEY Target key name already exists.' or e.message == 'Target key name is busy.'):
                    already_existing += 1
                else:
                    print 'Key failed:', key, `data`, `result`
                    raise e

        if cursor == 0:
            break

        cnt += len(keys)
        pbar.update(min(size, cnt))

    pbar.finish()
    print 'Keys disappeared on source during scan:', non_existing
    print 'Keys already existing on destination:', already_existing

if __name__ == '__main__':
    migrate()
