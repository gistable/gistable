#!python3.4
import io
import os
import sys
import mimetypes
import uuid

# Import the email modules we'll need
from email import policy
from email.parser import BytesParser

myfiles = ['20140217-0121.eml.1c2dffd0',
'20140217-0314.eml.14bac63d',
'20140218-0722.eml.00fe7528',
'20140219-0541.eml.74741be1',
'20140219-0543.eml.1c20938f',
'20140219-0608.eml.02af7d91',
'20140219-0612.eml.0d9a2c0b',
'20140224-2004.eml.6f36a877',
'20140225-1702.eml.39a4225b']

for filename in myfiles:
    msg = BytesParser(policy=policy.default).parse(open(filename, 'rb'))
    print('Processing %s' % (filename,))

    for attachment in msg.iter_attachments():
        fn = attachment.get_filename()
        print('Attachment filename is %s' % (fn,))
        if fn:
            extension = os.path.splitext(attachment.get_filename())[1]
        else:
            extension = mimetypes.guess_extension(attachment.get_content_type())
        f = io.BytesIO()
        data = attachment.get_content()
        with open(fn, 'wb') as f:
            if isinstance(data, str):
                # data is a string
                f.write(data.encode('utf-8'))
            else:
                # data is bytes
                f.write(data)
