"""Reads a har file from the filesystem, converts to CSV, then dumps to
stdout.
"""
import argparse
import json
from urlparse import urlparse


def main(harfile_path):
    """Reads a har file from the filesystem, converts to CSV, then dumps to
    stdout.
    """
    harfile = open(harfile_path)
    harfile_json = json.loads(harfile.read())
    i = 0

    for entry in harfile_json['log']['entries']:
        i = i + 1
        url = entry['request']['url']
        urlparts = urlparse(entry['request']['url'])
        size_bytes = entry['response']['bodySize']
        size_kilobytes = float(entry['response']['bodySize'])/1024
        mimetype = 'unknown'
        if 'mimeType' in entry['response']['content']:
            mimetype = entry['response']['content']['mimeType']

        print '%s,"%s",%s,%s,%s,%s' % (i, url, urlparts.hostname, size_bytes,
                                       size_kilobytes, mimetype)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        prog='parsehar',
        description='Parse .har files into comma separated values (csv).')
    argparser.add_argument('harfile', type=str, nargs=1,
                        help='path to harfile to be processed.')
    args = argparser.parse_args()

    main(args.harfile[0])