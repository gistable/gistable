#!/usr/bin/env python
#
# This script updates a field for all documents in a view. Modify as needed.
#
# This script requires couchdbkit:
# $ sudo easy_install -U Couchdbkit

from couchdbkit import Server
import logging

# Configuration

server_url = "http://example.com:5984"
database = "database"
view = "design_name/view_name"
field = "field_name"
old_value = "old_value"
new_value = "new_value"

# Program

logging.basicConfig(level=logging.INFO)
server = Server(server_url)
db = server.get_or_create_db(database)
entries_to_process = db.view(view, key=old_value, reduce=False, include_docs=True)
for entry in entries_to_process:
  doc = entry["doc"]
  doc[field] = new_value
  db.save_doc(doc)