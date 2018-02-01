# Python gzip demo: create and unpack archive

import os
import random
import string
import glob
import tarfile
import shutil
import filecmp


def get_random_word(length):
    return "".join([random.choice(string.letters + string.digits)
        for i in xrange(length)])


def get_random_text(length):
    total_length = 0
    words = []

    while total_length < length:
        words.append(get_random_word(random.randint(2, 15)))
        total_length = total_length + len(words[-1]) + 1

    return " ".join(words)[:length]


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def create_source_files(source_path, size):
    shutil.rmtree(source_dir)
    create_dir(source_path)
    for i in range(10):
        f = file(os.path.join(source_dir, str(i) + ".txt"), "wt")
        f.write(get_random_text(size))
        f.close()


def okay():
    print("Done.\n")


source_dir = "./source"
dest_dir = "./unpacked"
source_file_size = 65536
archive_name = "archive.tar.gz"


print("Creating source file with random text...")
create_source_files(source_dir, source_file_size)
okay()

print("Compressing files to %s..." % archive_name)
tar = tarfile.open(archive_name, "w:gz")
for file_name in glob.glob(os.path.join(source_dir, "*")):
    print("  Adding %s..." % file_name)
    tar.add(file_name, os.path.basename(file_name))
tar.close()
okay()

print("Decompressing files to %s..." % dest_dir)
shutil.rmtree(dest_dir)
create_dir(dest_dir)
tar = tarfile.open(archive_name, "r:gz")
for tarinfo in tar:
    print "  Extracting %s (size: %db; type: %s)..." % (tarinfo.name,
        tarinfo.size, "regular file" if tarinfo.isreg() else "directory"
        if tarinfo.isdir() else "something else")
    tar.extract(tarinfo, dest_dir)
tar.close()
okay()

print("Comparing source and result...")
dc = filecmp.dircmp(source_dir, dest_dir)
print("Same: [%s]" % ", ".join(dc.same_files))
print("Different: [%s]" % ", ".join(dc.diff_files))
print("Funny: [%s]" % ", ".join(dc.funny_files))

print("Test passed." if len(dc.diff_files) == 0
    and len(dc.funny_files) == 0 else "Test failed.")
