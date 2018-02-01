# vim: set fileencoding=utf-8 :
#
# How to store and retrieve gzip-compressed objects in AWS S3
###########################################################################
#
#   Copyright 2015 Vince Veselosky and contributors
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
from __future__ import absolute_import, print_function, unicode_literals
from io import BytesIO
from gzip import GzipFile

import boto3
s3 = boto3.client('s3')
bucket = 'bluebucket.mindvessel.net'

# Read in some example text, as unicode
with open("utext.txt") as fi:
    text_body = fi.read().decode("utf-8")

# A GzipFile must wrap a real file or a file-like object. We do not want to
# write to disk, so we use a BytesIO as a buffer.
gz_body = BytesIO()
gz = GzipFile(None, 'wb', 9, gz_body)
gz.write(text_body.encode('utf-8'))  # convert unicode strings to bytes!
gz.close()
# GzipFile has written the compressed bytes into our gz_body
s3.put_object(
    Bucket=bucket,
    Key='gztest.txt',  # Note: NO .gz extension!
    ContentType='text/plain',  # the original type
    ContentEncoding='gzip',  # MUST have or browsers will error
    Body=gz_body.getvalue()
)
retr = s3.get_object(Bucket=bucket, Key='gztest.txt')
# Now the fun part. Reading it back requires this little dance, because
# GzipFile insists that its underlying file-like thing implement tell and
# seek, but boto3's io stream does not.
bytestream = BytesIO(retr['Body'].read())
got_text = GzipFile(None, 'rb', fileobj=bytestream).read().decode('utf-8')
assert got_text == text_body
