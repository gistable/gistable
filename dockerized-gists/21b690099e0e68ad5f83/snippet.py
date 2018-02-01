import mailbox
from collections import defaultdict
from flanker import mime
from flanker.addresslib import address

mbox_path = '...'
mbox = mailbox.mbox(mbox_path)

domains = defaultdict(int)

items = mbox.iteritems()
for msg in items:
    raw_msg = msg[1].as_string()
    parsed = mime.from_string(raw_msg)
    from_header = parsed.headers['From']
    from_domain = address.parse(from_header).hostname
    domains[from_domain] += 1