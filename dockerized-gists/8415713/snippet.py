#!/usr/bin/env python
import os
import sys
import shutil
import subprocess


class UserError(Exception):
    pass


def move_to_num(destroot, name, zoom, folder):
    x = os.path.basename(folder)
    num = int(x[1] if x.startswith('-') else x[0])
    dst_dir = os.path.join(destroot, '%s-%s' % (name, num), '%s' % zoom)
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    print "Move %s to %s" % (folder, dst_dir)
    shutil.move(folder, dst_dir)


def split_tiles(folder, destroot):
    if not os.path.isdir(folder):
        raise UserError('%s is not a folder.' % folder)

    metadata = os.path.join(folder, 'metadata.json')
    if not os.path.exists(metadata):
        raise UserError('%s missing.' % metadata)

    name = os.path.basename(folder)

    for z in os.listdir(folder):
        path = os.path.join(folder, z)
        if os.path.isdir(path):
            for x in os.listdir(path):
                move_to_num(destroot, name, int(z), os.path.join(folder, z, x))

    for i in range(10):
        namenum = '%s-%s' % (name, i)
        dst_dir = os.path.join(destroot, namenum)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        shutil.copy(metadata, dst_dir)
        mbtiles = os.path.join(destroot, namenum) + '.mbtiles'
        if os.path.exists(mbtiles):
            os.remove(mbtiles)
        subprocess.call(['mb-util', dst_dir, mbtiles])


if __name__ == '__main__':
    try:
        folder = sys.argv[1]
        split_tiles(folder, '.')
    except IndexError:
        print "Usage: %s FOLDER" % sys.argv[0]
        sys.exit(1)
    except UserError as e:
        print e
        sys.exit(2)
    except Exception as e:
        raise
        print "There was an unexpected error. To merge again all folder into one, just do:\n\n    cp -R %(f)s-?/* %(f)s/ && rm -rf %(f)s-?;\n" % {'f':folder}
