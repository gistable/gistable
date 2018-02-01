####################################################
# WARNING: This is very hacky! Use at your own risk.
#
# This assumes you have all keys in a single DB and
# want to move them all to DB 0. If you have keys
# in more than one DB, the first DB found will be
# rewritten to 0, with all others left alone.
####################################################

import shutil
def rewrite_rdb(source_file):
    new_file = '%s.new' % source_file
    backup_file = '%s.backup' % source_file
    src = open(source_file, 'rb')
    dst = open(new_file, 'wb')
    # rdb header info and the SELECT statement
    dst.write(src.read(10))
    # write a binary 0, indicating DB:0
    dst.write('\x00')
    # read the byte containing the existing DB
    # we don't need it.
    _ = src.read(1)
    # move all the rest of the data
    buf = src.read(4096)
    while len(buf):
        dst.write(buf)
        buf = src.read(4096)
    src.close()
    dst.close()
    shutil.move(source_file, backup_file)
    shutil.move(new_file, source_file)
