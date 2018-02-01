#!/usr/bin/env python
# Convert files in Open Container Format from Traditional Chinese
# to Simplified Chinese.

import sys, os, zipfile, re, codecs, subprocess
from xml.dom import minidom

sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
debug = True

def find_output_path(input_path):
    candidate = os.path.splitext(input_path)[0]
    if os.path.exists(candidate):
        # Quick shortcut for debugging, do not attempt to extract
        # the file again, reuse the extracted directory.
        if debug and os.path.isdir(candidate):
            return candidate
        match = re.match('(.*)-(\d+)', candidate)
        if match:
            print match.group(1)
            candidate = match.group(1)
            digit = int(match.group(2)) + 1
        else:
            digit = 1
        candidate = "%s-%d" % (candidate, digit)
        return find_output_path(candidate)
    return candidate

def find_opf_path(input_path):
    metadata_file = os.path.join(input_path, "META-INF", "container.xml")
    if os.path.isfile(metadata_file):
        metadata = minidom.parse(metadata_file)
        root_files = metadata.getElementsByTagName('rootfile')
        if len(root_files):
            opf_file = root_files[0].attributes['full-path'].value
            opf_path = os.path.join(input_path, opf_file)
            if os.path.isfile(opf_path):
                return opf_path
    return None

def find_files_to_convert(input_path, opf_path):
    opf = minidom.parse(opf_path)
    items = opf.getElementsByTagName('item')
    files = []
    types = ['application/x-dtbncx+xml', 'application/xhtml+xml']
    for item in items:
        media_type = item.attributes['media-type'].value
        if media_type in types:
            href = item.attributes['href'].value
            path = os.path.join(input_path, href)
            if os.path.isfile(path):
                files.append(path)
    return files

def convert_files_in_place(files):
    for f in files:
        output_file = '%s.tmp' % f
        cmd = "opencc -i '%s' -o '%s' -c zht2zhs.ini" % (f, output_file)
        print 'Converting file: %s' % f
        os.system(cmd.encode('utf-8'))
        os.rename(output_file, f)

def repack_files(input_path):
    output_file_path = "%s.epub" % input_path
    if os.path.isfile(output_file_path):
        (trunk, ext) = os.path.splitext(output_file_path)
        old_file_path = "%s.old%s" % (trunk, ext)
        print "Renaming existing file to %s" % old_file_path
        os.rename(output_file_path, old_file_path)
    print "Repacking converted files into %s" % output_file_path
    cmd_args = [ 'zip', '-r', output_file_path, '.']
    p = subprocess.Popen(cmd_args, cwd=input_path)
    p.wait()
    print "Removing temporary directory %s" % input_path
    cmd = "rm -rf '%s'" % input_path
    os.system(cmd.encode('utf-8'))

if len(sys.argv) < 2:
    print "usage: %s <book.epub|book.mobi|book directory>"
    sys.exit(1)

input_path = sys.argv[1].decode('utf-8')
if not os.path.isdir(input_path):
    output_path = find_output_path(input_path)
    if not (debug and os.path.isdir(output_path)):
        print "Try extracting %s to %s" % (input_path, output_path)
        zipfile = zipfile.ZipFile(input_path)
        zipfile.extractall(output_path)
    input_path = output_path

opf_path = find_opf_path(input_path)

if opf_path:
    files = find_files_to_convert(input_path, opf_path)
    if len(files):
        convert_files_in_place(files)
    repack_files(input_path)
else:
    print "Not in Open Container Format, abort."
    sys.exit(1)
