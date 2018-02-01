#!/usr/bin/env python

###
# Takes a username from environment variable PAM_USER, a password from STDIN
# and tries to verify the shadow's password using LDAP's SSHA algorithm:
#
#    {SSHA}...base64encodedString...
#
# If used within PAM auth this provides a compatibility layer that allows
# to migrate LDAP user into Unix user accounts. When the user's password
# has been verified the program will execute 'passwd' to convert the password
# into the system's default format. This means this program will make itself
# obsolete when every user has logged in at least once.
#
# This programm will exit with return code 1, except when the password
# has been verified.
#
# To integrate it into PAM, open /etc/pam.d/common-auth and replace the line:
#
#    auth   [success=1 default=ignore] pam_unix.so nullok_secure
#    auth   requisite                  pam_deny.so
#
# with
#
#    auth   [success=2 default=ignore] pam_unix.so nullok_secure
#    auth   [success=1 default=ignore] pam_exec.so expose_authtok /usr/local/sbin/verify_ssha_passwd
#    auth   requisite                  pam_deny.so
#
# Author: Roland Tapken <rt@tasmiro.de>
# Article: http://rolandtapken.de/blog/2016-03/migrate-user-accounts-openldap-unix-system-user
###

import os
import sys
import hashlib
import subprocess
from base64 import urlsafe_b64decode as decode

def checkPassword(challenge_password, password):
    challenge_bytes = decode(challenge_password[6:])
    digest = challenge_bytes[:20]
    salt = challenge_bytes[20:]
    hr = hashlib.sha1(password)
    hr.update(salt)
    return digest == hr.digest()

def updatePassword(username, password):
    proc=subprocess.Popen(['passwd', '--', username], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.stdin.write(password)
    proc.stdin.write('\n')  
    proc.stdin.write(password)
    proc.stdin.flush()  
    proc.communicate() 

try:
    user=os.environ.get('PAM_USER')
    if user:
        shadow=subprocess.Popen(['getent', 'shadow', '--', user], shell=False, stdout=subprocess.PIPE).stdout.read()
        if shadow:
            challenge=shadow.split(':')[1]
            if challenge and challenge.startswith('{SSHA}'):
                for password in sys.stdin:
                    # Shell (testing) terminates the string with \n or \r,
                    # pam terminates it with \0. Of course this means you
                    # cannot use \n or \r as last character of a password ;-)
                    password=password.rstrip('\n\r\0')
                    if checkPassword(challenge, password):
                        # Try to update the user's password into the system's default hash
                        try:
                            updatePassword(user, password)
                        except:
                            # Ignore if this is not possible
                            pass
                        os._exit(0)
    os._exit(1)
except:
    sys.exit(1)