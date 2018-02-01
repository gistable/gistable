''' quick example showing how to attach a pdf to multipart messages
and then send them from SES via boto
'''

from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

import boto

# via http://codeadict.wordpress.com/2010/02/11/send-e-mails-with-attachment-in-python/
msg = MIMEMultipart()
msg['Subject'] = 'weekly report'
msg['From'] = 'robot@gmail.com'
msg['To'] = 'admin@gmail.com'

# what a recipient sees if they don't use an email reader
msg.preamble = 'Multipart message.\n'

# the message body
part = MIMEText('Howdy -- here is the data from last week.')
msg.attach(part)

# the attachment
part = MIMEApplication(open('/tmp/weekly.pdf', 'rb').read())
part.add_header('Content-Disposition', 'attachment', filename='weekly.pdf')
msg.attach(part)

# connect to SES
connection = boto.connect_ses(aws_access_key_id='ID123'
    , aws_access_key_secret='secret456')

# and send the message
result = connection.send_raw_email(msg.as_string()
    , source=msg['From']
    , destinations=[msg['To']])
print result