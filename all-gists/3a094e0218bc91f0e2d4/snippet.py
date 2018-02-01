# Copyright 2014 Zilverline B.V.

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


# Put this code in filter_plugins/custom_plugins.py
#
# Tested with keyczar 0.71c. To create a keystore with keyczar do:
#
# keyczart create --location=$HOME/.my-keyczar-keystore --purpose=crypt 
# keyczart addkey --location=$HOME/.my-keyczar-keystore --status=primary 
#
# Allows for property and file based encryption.
# Example:
# group_vars/development
#   encrypted_property = AADFGASDGdsfkjasg
#   unencrypted_property = www.zilverline.com
#
# Usage in e.g. task: password={{ encrypted_property | vault }}
#
# Example usage for file encryption
#
# - name: Install certificate key
#  copy: content="{{ lookup('file', 'private.key.encrypted') | vault }}" dest=/etc/ssl/certs/private.key owner=root group=root mode=0600

def vault(encrypted):
  method = """
from keyczar import keyczar
import os.path
import sys
keydir = os.path.expanduser('~/.my-keyczar-keystore')
crypter = keyczar.Crypter.Read(keydir)
sys.stdout.write(crypter.Decrypt("%s"))
  """ % encrypted
  from subprocess import check_output
  return check_output(["python", "-c", method])

class FilterModule(object):

  def filters(self):
    return {
      'vault': vault
    }

# Put this code in scripts/encrypt.sh
#
# This allows to encrypt individual values to use e.g. in group_var files
# Usage:
# - To encrypt: scripts/encrypt.sh
# - To decrypt: scripts/encrypt.sh -d
#!/usr/bin/env python
import os.path
import getpass
from optparse import OptionParser
from keyczar import keyczar

parser = OptionParser()
parser.add_option("-d", "--decrypt", action="store_true", help="decrypt the input", dest="decrypt")

(options, args) = parser.parse_args()

keydir = os.path.expanduser('~/.my-keyczar-keystore')
crypter = keyczar.Crypter.Read(keydir)

if options.decrypt:
  encrypted_input = raw_input("Type the encrypted string: ")
  print 'The decrypted secret: %s' % crypter.Decrypt(encrypted_input)
else:
  password = getpass.getpass('Type the secret you want to encrypt: ')
  encrypted_secret = crypter.Encrypt(password)
  print 'The encrypted secret: %s' % encrypted_secret

# Put this code in scripts/encrypt-file.sh
#
# This allows to encrypt entire files e.g. private key files.
# Usage:
# - To encrypt: scripts/encrypt-file.sh -f FILE_TO_ENCRYPT
# - To decrypt: scripts/encrypt-file.sh -d -f FILE_TO_DECRYPT
#!/usr/bin/env python
import os.path
from optparse import OptionParser
from keyczar import keyczar

parser = OptionParser()
parser.add_option("-f", "--file", help="the input file", dest="filename", metavar="FILE")
parser.add_option("-d", "--decrypt", action="store_true", help="decrypt the file", dest="decrypt")

(options, args) = parser.parse_args()

if options.filename:
  with open(options.filename, 'r') as content_file:
    content = content_file.read()
    keydir = os.path.expanduser('~/.my-keyczar-keystore')
    crypter = keyczar.Crypter.Read(keydir)
    if options.decrypt:
      print crypter.Decrypt(content)
    else:
      encrypted_secret = crypter.Encrypt(content)
      print encrypted_secret
else:
  parser.print_help()
