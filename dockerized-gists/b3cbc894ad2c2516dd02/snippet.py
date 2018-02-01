#!/usr/bin/env python

import sys
import urllib
import urlparse
import base64
import mimetypes
import cgi

from os import path

import sqlite3

# More info (typical that I find this stuff after starting...):
# https://github.com/kyro38/MiscStuff/blob/master/OSXStuff/iMessageBackup.sh

# TODO:
# - Itterate over available chats
# - Split into days
# - Handle multiple runs (don't trash existing data)
# - Add auto-linking
# - Export media (or use base64 encoding)
# - Allow selective export
# - Match chat IDs up to names using Contacts.app SQLite db

CHAT_DB = path.expanduser("~/Library/Messages/chat.db")

# Apple's epoch starts on January 1st, 2001 for some reason...
# cf. http://apple.stackexchange.com/questions/114168
EPOCH=978307200

def list_chats():
    db = sqlite3.connect(CHAT_DB)
    cursor = db.cursor()
    rows = cursor.execute("""
        SELECT chat_identifier
          FROM chat;
    """)
    for row in rows:
        print(row[0])

def export(chat_id, date):
    db = sqlite3.connect(CHAT_DB)
    cursor = db.cursor()

    # @@ pull date calculations out of SQLite
    rows = cursor.execute("""
          SELECT datetime(m.date + ?, 'unixepoch', 'localtime') as fmtdate,
                 m.is_from_me,
                 m.text,
                 a.filename
            FROM chat as c
      INNER JOIN chat_message_join AS cm
              ON cm.chat_id = c.ROWID
      INNER JOIN message AS m
                 ON m.ROWID = cm.message_id
       LEFT JOIN message_attachment_join AS ma
              ON ma.message_id = m.ROWID
       LEFT JOIN attachment as a
              ON a.ROWID = ma.attachment_id
           WHERE c.chat_identifier = ?
             AND fmtdate LIKE ?
        ORDER BY m.date;
    """, (EPOCH, chat_id, date))

    print("""
    <meta charset=\"utf-8\">

    <style>
    body { margin: 0; padding: 0; }
    .message {
        white-space: pre-wrap;
        max-width: 800px;
        padding: 10px;
        margin: 10px;
    }
    .me { background-color: #A6DBFF; }
    .buddy { background-color: #EEE; }
    .message img { max-width: 800px; }
    </style>
    """)

    for row in rows:
        date = row[0]
        who = "me" if row[1] is 1 else "buddy"
        if row[3]:
            attachment = path.expanduser(row[3])
            media_type = mimetypes.guess_type(attachment)[0]
            with open(attachment, "rb") as image:
                encoded_data = base64.b64encode(image.read())
            text = "<img src=\"data:%s;base64,%s\">" % (
                media_type, encoded_data)
        else:
            text = row[2]
        line = "<div class=\"message %s\" title=\"%s\">%s</div> " % (
            who, date, cgi.escape(text))
        print(line.encode("utf8"))

def main():
    # @@ Output some sort of help
    if len(sys.argv) == 1:
        list_chats()
        sys.exit()
    chat_id = None
    if len(sys.argv) > 1:
        chat_id = sys.argv[1]
    date = None
    if len(sys.argv) > 2:
        date = sys.argv[2]
    if len(sys.argv) > 3:
        # @@ Handle errors gracefully
        sys.exit()
    export(chat_id, date)

if __name__ == "__main__":
    main()
