# encoding=utf-8

import sys
import datetime
import email
import mimetypes
import os
import time
import gzip
import subprocess

from cStringIO import StringIO

from boto.s3.connection import S3Connection

s3 = S3Connection()

GZIP_CONTENT_TYPES = (
    'text/css',
    'application/javascript',
)

GZIP_SIZE_MIN = 1024  # Per recommendation

EXCLUDE_FILENAMES = ('.DS_Store', '.git')

HEADERS = {
    # HTTP/1.0
    'Expires': '%s GMT' % (email.Utils.formatdate(
        time.mktime((datetime.datetime.now() +
            datetime.timedelta(days=365 * 2)).timetuple()))),
    # HTTP/1.1
    'Cache-Control': 'max-age %d' % (3600 * 24 * 365 * 2),
}


def main():
    try:
        media_root, bucket_root = sys.argv[1:]
    except ValueError:
        sys.exit(u"Error. (Hint: python sync_s3.py public/ s3.bucket.com/static )")

    if '/' in bucket_root:
        bucket_name, prefix = bucket_root.split("/", 1)
    else:
        bucket_name, prefix = bucket_root, ''

    bucket = s3.get_bucket(bucket_name)

    # tar c dir | md5sum
    media_root_md5, stderr = subprocess.Popen('tar c %s | md5' % media_root,
        stdout=subprocess.PIPE, shell=True).communicate()
    if stderr:
        raise Exception(u'Could not get unique folder checksum')

    s3_root = os.path.join(
        prefix,
        media_root_md5[:6],
    )

    if not media_root.endswith("/"):
        # We want to copy folder as a whole, not just contents - like rsync
        s3_root = os.path.join(s3_root, media_root)

    s3_root = s3_root.rstrip("/")  # Normalize

    print "Uploading to //s3.amazonaws.com/%s/%s/" % (bucket_name, s3_root)

    for root, dirs, files in os.walk(media_root):
        for filename in files:
            if [s for s in EXCLUDE_FILENAMES if root.endswith(s)]:
                continue  # example .git
            if filename in EXCLUDE_FILENAMES:
                continue  # example .DS_Store

            path = os.path.join(root, filename)
            s3_path = os.path.join(os.path.relpath(root, media_root), filename)
            s3_path = os.path.normpath(os.path.join(s3_root, s3_path))

            content_type, _ = mimetypes.guess_type(s3_path)
            byte_length = os.stat(path).st_size
            headers = HEADERS.copy()
            key = bucket.new_key(s3_path)

            with file(path) as fp:

                if content_type in GZIP_CONTENT_TYPES and byte_length > GZIP_SIZE_MIN:
                    headers['Content-Encoding'] = 'gzip'
                    compressed = StringIO()
                    with gzip.GzipFile(fileobj=compressed, mode='wr', compresslevel=9) as gzip_fp:
                        gzip_fp.write(fp.read())
                    contents = compressed.getvalue()

                else:
                    contents = fp.read()

            if content_type:
                headers['Content-Type'] = content_type

            if os.environ.get('DRYRUN') == "true":
                for key, value in headers.items():
                    print "%s: %s" % (key, value)
                print s3_path
                print

            else:
                key.set_contents_from_string(
                    contents, headers, replace=True, policy='public-read')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(u"Early exit")
