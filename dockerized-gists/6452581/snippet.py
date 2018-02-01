conf = {
  "sqs-access-key": "",
  "sqs-secret-key": "",
  "sqs-queue-name": "",
  "sqs-region": "us-east-1",
  "sqs-path": "sqssend"
}

import boto.sqs
conn = boto.sqs.connect_to_region(
        conf.get('sqs-region'),
        aws_access_key_id               = conf.get('sqs-access-key'),
        aws_secret_access_key   = conf.get('sqs-secret-key')
)

q = conn.create_queue(conf.get('sqs-queue-name'))

from boto.sqs.message import RawMessage
m = RawMessage()
m.set_body('Reader started at this point.')
retval = q.write(m)
print 'added message, got retval: %s' % retval

import time
while(True):
        for m in q.get_messages():
                print '%s: %s' % (m, m.get_body())
                q.delete_message(m)
        time.sleep(1)