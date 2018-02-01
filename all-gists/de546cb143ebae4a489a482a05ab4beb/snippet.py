#! /usr/bin/env python
#
# Author: Gaute Hope <eg@gaute.vetsj.com> / 2017-10-08

import os, sys, os.path
import subprocess
import notmuch
import email
import email.parser
import email.policy
import shlex
import json

thread = sys.argv[1]
mid    = sys.argv[2] if len(sys.argv) > 2 else None

print ("ght: searching for github reference in:", thread, "( message:", mid, ")")

def find_script (fname):
  """
  New GitHub messages contain a JSON part with the information.
  """
  with open(fname, 'rb') as f:
    msg = email.message_from_binary_file (f)

    for part in msg.walk ():
      if part.get_content_type() == "text/html":
        p = part.get_payload (decode = True).decode ('UTF-8')
        key = '<script type="application/json" data-scope="inboxmarkup">'
        script = p.rfind (key)
        script = p[script+len(key):p.find('</script>', script)]

        j = json.loads (script)
        return j['updates']['action']['url']

def scan_message (m, generic):
  with open (m.get_filename(), 'rb') as f:
    headers = email.parser.BytesParser(policy=email.policy.default).parse(f)

  print ("scanning:", m, headers.get('Message-Id'), "generic:", generic)

  s = headers.get('X-GitHub-Sender', None)
  if s is None: return None

  url = find_script (m.get_filename())
  if url is None:
    print ("ght: old issue, falling back manually scanning email..")
    if generic:
      ref = headers.get('In-Reply-To').split ('@')[0][1:]
      url = 'https://github.com/' + ref # fallback
    else:
      ref = headers.get('In-Reply-To').split ('@')[0][1:]
      mid  = headers.get('Message-Id').split('@')[0][1:]
      cmnt = os.path.basename (mid)
      url = 'https://github.com/' + ref + "#issuecomment-" + cmnt

  return url


def open_url (u):
  print ("opening: ", u)

  p = subprocess.Popen (['xdg-open', u ], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)

db = notmuch.Database()

if mid is not None:
  print ("ght: first trying message..")
  m = db.find_message (mid)
  if m is not None:
    url = scan_message (m, False)
    if url:
      open_url (url)
      sys.exit (1) # non-zero to avoid updating thread

      # fall through to thread if not found..
  print ("ght: could not find url in message, trying thread..")

q = db.create_query ("thread:" + thread)

# scanning oldest message first should give us generic url.
q.set_sort (notmuch.Query.SORT.OLDEST_FIRST)

msgs = q.search_messages ()
for m in msgs:
  # take first message
  url = scan_message (m, True)
  if url:
    open_url (url)
    break

# we have to do this so that the query object is not gc'ed before its dependents and we
# get a segfault.
del m
del msgs
del q

db.close ()

sys.exit (1) # non-zero to avoid updating thread
