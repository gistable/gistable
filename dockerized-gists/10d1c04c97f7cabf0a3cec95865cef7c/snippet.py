#coding: utf-8
# Please install [fastlane](https://github.com/fastlane/fastlane) first.

import os

bundle_identifier = "xxx"
itunes_user = "yyy"
emails = """
a@gmail.com
b@gmail.com
"""

def invite(email):
  command = 'pilot add %s -a %s -u %s' % (email, bundle_identifier, itunes_user)
  print command
  output = os.popen(command)
  print output.read()

if __name__ == '__main__':
  email_array = emails.split("\n")
  for email in email_array:
    if len(email):
      invite(email)
