#!/usr/bin/env python
import imaplib
import os
import logging
import optparse

# LABEL = 'support'
# QUERY = 'before:2015-06-01 -label:to-delete'
# DEST  = 'to-delete'
LABEL = 'to-delete'
QUERY = None
DEST  = '[Gmail]/Trash'

logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s] %(levelname)s %(message)s")

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login('nelhage@stripe.com', os.environ['GMAIL_PASSWORD'])
logging.info("Logged in.")
status, n = mail.select(LABEL)
logging.info("SELECTED %s, found %s messages...", LABEL, n[0])
if QUERY:
    search_args = ('X-GM-RAW', QUERY)
else:
    search_args = ('ALL',)
status, ids = mail.uid('search', None, *search_args)
if not ids[0]:
    logging.info("search returned no UIDs")
    os.exit(0)

ids = ids[0].split(' ')
logging.info("Fetched %s UIDs...", len(ids))

def flush():
    global did_delete
    mail.uid('copy', ','.join(batch), DEST)
    did_delete += len(batch)
    del batch[:]
    logging.info("flagged %d messages...", did_delete)

did_delete = 0
batch = []
for i in ids:
    batch.append(i)
    if len(batch) >= 100:
        flush()

flush()
