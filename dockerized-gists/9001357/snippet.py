#!/usr/bin/env python
"""
Extract all attachments from MS Outlook '.eml' file EML_FILE into
directory OUTPUT_DIR. If OUTPUT_DIR does not exist, it will be
created.

Usage: extract_attachments.py EML_FILE OUTPUT_DIR
"""
import sys
import os
import os.path
from collections import defaultdict
from email.parser import Parser

def parse_message(filename):
    with open(filename) as f:
        return Parser().parse(f)

def find_attachments(message):
    """
    Return a tuple of parsed content-disposition dict, message object
    for each attachment found.
    """
    found = []
    for part in message.walk():
        if 'content-disposition' not in part:
            continue
        cdisp = part['content-disposition'].split(';')
        cdisp = [x.strip() for x in cdisp]
        if cdisp[0].lower() != 'attachment':
            continue
        parsed = {}
        for kv in cdisp[1:]:
            key, val = kv.split('=')
            if val.startswith('"'):
                val = val.strip('"')
            elif val.startswith("'"):
                val = val.strip("'")
            parsed[key] = val
        found.append((parsed, part))
    return found

def run(eml_filename, output_dir):
    msg = parse_message(eml_filename)
    attachments = find_attachments(msg)
    print "Found {0} attachments...".format(len(attachments))
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    for cdisp, part in attachments:
        cdisp_filename = os.path.normpath(cdisp['filename'])
        # prevent malicious crap
        if os.path.isabs(cdisp_filename):
            cdisp_filename = os.path.basename(cdisp_filename)
        towrite = os.path.join(output_dir, cdisp_filename)
        print "Writing " + towrite
        with open(towrite, 'wb') as fp:
            data = part.get_payload(decode=True)
            fp.write(data)


def main():
    args = sys.argv[1:]
    if len(args) != 2:
        print 'Usage: extract_attachments.py EML_FILE OUTPUT_DIR'
        sys.exit(1)
    filename, outdir = args
    run(filename, outdir)


if __name__ == '__main__':
    main()
