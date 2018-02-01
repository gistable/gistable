from io import BytesIO
import gzip
import shutil


def upload_gzipped(bucket, key, fp, compressed_fp=None, content_type='text/plain'):
    """Compress and upload the contents from fp to S3.

    If compressed_fp is None, the compression is performed in memory.
    """
    if not compressed_fp:
        compressed_fp = BytesIO()
    with gzip.GzipFile(fileobj=compressed_fp, mode='wb') as gz:
        shutil.copyfileobj(fp, gz)
    compressed_fp.seek(0)
    bucket.upload_fileobj(
        compressed_fp,
        key,
        {'ContentType': content_type, 'ContentEncoding': 'gzip'})


def download_gzipped(bucket, key, fp, compressed_fp=None):
    """Download and uncompress contents from S3 to fp.

    If compressed_fp is None, the compression is performed in memory.
    """
    if not compressed_fp:
        compressed_fp = BytesIO()
    bucket.download_fileobj(key, compressed_fp)
    compressed_fp.seek(0)
    with gzip.GzipFile(fileobj=compressed_fp, mode='rb') as gz:
        shutil.copyfileobj(gz, fp)


import boto3
from tempfile import TemporaryFile
from io import BytesIO

s3 = boto3.resource('s3')
bucket = s3.Bucket('test')  # CHANGE ME

def example1(bucket):
    """In memory compression"""
    with open('foo.txt', 'rb') as fp:
        upload_gzipped(bucket, 'test.txt', fp)

    with open('bar.txt', 'wb') as fp:
        download_gzipped(bucket, 'test.txt', fp)

def example2(bucket):
    """Using a temporary file for compression"""
    with open('foo.txt', 'rb') as fp, TemporaryFile() as helper_fp:
        upload_gzipped(bucket, 'test.txt', fp, compressed_fp=helper_fp)

    with open('bar.txt', 'wb') as fp, TemporaryFile() as helper_fp:
        download_gzipped(bucket, 'test.txt', fp, compressed_fp=helper_fp)

# Some actual tests
original = BytesIO(b'Jackdaws love my big sphinx of quartz.')
original.seek(0)
upload_gzipped(bucket, 'test.txt', original)

gzipped = BytesIO()
bucket.download_fileobj('test.txt', gzipped)

assert original.getvalue() != gzipped.getvalue()

ungzipped = BytesIO()
download_gzipped(bucket, 'test.txt', ungzipped)

assert original.getvalue() == ungzipped.getvalue()
