#!/usr/bin/python

import os
import hashlib

mypasswords = [
  "doors",
  "d00rs",
  "Morrison",
  "Hotel"
]

pwned_passwords_files = [
  "pwned-passwords-update-1.txt",
  "pwned-passwords-update-2.txt",
  "pwned-passwords-1.0.txt"
]

def getFileSize(filename):
  return os.path.getsize(filename)

def getLineLength(filename):
  with open(filename, "r") as file:
    line = file.readline()
    return file.tell()

def searchForPass(password):
  pass_hash = hashlib.sha1(password).hexdigest().upper()
  print("\nSearching for SHA1 hash: %s" % pass_hash)
  for password_file in pwned_passwords_files:
    print("Searching in: %s" % password_file)

    filesize = getFileSize(password_file)
    line_length = getLineLength(password_file)
    line_number = filesize / line_length
    # print("File size is: %s bytes, line length is %s bytes, line number is %s" % (filesize, line_length, line_number))
    pos_from = 0
    pos_to = line_number

    with open(password_file, "r") as file:
      while True:
        current_pos = (pos_to + pos_from) / 2
        file.seek(current_pos * line_length)
        line = file.readline()
        pwned_hash = line.strip()
        # print("Go to %s line %s" % (pwned_hash, current_pos))

        if pwned_hash == pass_hash:
          print("Found: '%s' as %s" % (password, pwned_hash))
          return

        if abs(pos_to - pos_from) < 1:
          break

        if pwned_hash < pass_hash:
          pos_from = current_pos
          if abs(pos_to - pos_from) <= 1:
            pos_from = pos_to
        else:
          pos_to = current_pos
          if abs(pos_to - pos_from) <= 1:
            pos_to = pos_from

  print("Not found, all clear!")

for pwd in mypasswords:
  searchForPass(pwd)
