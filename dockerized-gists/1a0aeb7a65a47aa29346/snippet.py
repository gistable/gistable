#!/usr/bin/python

import hmac, struct, time, base64, hashlib  # for totp generation
import re, sys, subprocess                  # for general stuff
from getopt import getopt, GetoptError      # pretending to be easy-to-use


#
# gtb - Google(auth) + Tunnelblick
# 
# David Schuetz
# May 30, 2014
# http://darthnull.org/2014/05/30/google-auth-tunnelblick
#
# Using OS X keychain and python-based Google Auth library to automatically
# update Tunnelblick VPN credentials to simplify login to VPN
#
# May not acutally comply with corporate security policies stated or unstated.
# Use at own risk. :)
#
# Incorporates code adapted from https://github.com/tadeck/onetimepass
#   (simpler to just do the TOTP token generation internally and avoid
#   depending on an outside library)
# 


#
# SETUP:
#
#   1. Set up Tunnelblick to store credentials in keychain
#      Use your real userid, but some generic "fakepass" password
#   2. Note the Tunnelblick VPN name 
#      If it's "MyVPN.tblick" then the name is "MyVPN"
#   3. Run this script, using "--name <name> --setup"
#   4. When prompted, enter your VPN Password 
#   5. When prompted, enter your Google Authenticator key
#      Optionally, enter "none" and and the script will not calcualte
#      Google Auth OTP codes on the fly but will instead prompt at runtime
#   6. The script will print out all the sensitive info for debug purposes
#      Make sure it looks accurrate
#   7. Re-run the script, using just "--name" option
#      (or add --otp <tokencode> if you chose not to store Google Auth key)
#   8. If connection works fine, fix the Keychain Tunnelblick entries for
#      the connection (to password protect 'password' and 'auth-data')
#      (See security notice below for details)
#   


# -------------------------------------------------------------------------
# *** SECURITY NOTICE ***
# -------------------------------------------------------------------------
#
# Note that data stored in keychain will be readable by the command-line
#   application "security" without a password, provided the login keychain
#   is unlocked. An attacker with access to a logged-in terminal session for
#   the user who configured this may be able to extract login credentials.
#
# To mitigate this, after setup, examine the "auth-data" and "password"
#   entries for the Tunnelblick connection inside the Keychain Access 
#   application. Delete the "security" application from the "always allow 
#   access" list and check "Confirm + Ask for password" to force the user 
#   to enter their keychain (login) password.
#
# The "username" and "password" entries may have Tunnelblick configured for
#   "always allow access."
#

# -------------------------------------------------------------------------

# 
# If you want to hardcode the VPN name, do it here.
# 
NAME = ''

#
# -------------------------------------------------------------------------
# Shouldn't have to change anything after this, except maybe SERVICE_PREFIX
# -------------------------------------------------------------------------
#

# SERVICE_PREFIX - the keychain item's owner. in Tunnelblick, items are 
#   stored under "Tunnelblick-Auth-MyVpnName". You may be able to change 
#   this to support clients other than Tunnelblick.
#
# PASSWORD_DEST - similarly, this is where Tunnelblick puts the password
#   it will use to login. When the app calculates the new composite password
#   (base password + tokencode), this is where it's stuffed prior to 
#   launching the VPN client. Other clients may use a different name.
#

SERVICE_PREFIX = 'Tunnelblick-Auth-'  
PASSWORD_DEST = 'password'

# -------------------------------------------------------------------------

NOVPN = 0
SETUP = 0
DEBUG = 0

OTP = ''
keychain_service = ''


def main():
    global DEBUG, NOVPN, NAME, keychain_service

    parse_opts()

    keychain_service = '%s%s' % (SERVICE_PREFIX, NAME)

    if SETUP:
        run_setup()
        DEBUG = 1       # after setup is complete, print details but
        NOVPN = 1       #   don't actually connect vpn just yet

    auth_data = get_keychain_item(keychain_service, 'auth-data')

    try:
        google_key, vpn_password = auth_data.split(':', 1)
    except:
        google_key = ''
        vpn_password = ''

    if (auth_data == '') or (vpn_password == '') or (google_key == ''):
        print "\n  ** ERROR **\n"
        print "The Keychain entry for %s 'auth-data' is mising or damaged." % keychain_service
        print "You may need to re-run setup."
        sys.exit(1)

    if google_key == 'NONE':
        if OTP == '':
            print "Enter current Google Authenticator token code --> ",
            token = sys.stdin.readline().strip()
        else:
            token = OTP
    else:
        token = get_totp_token(google_key)

    new_pass = '%s%s' % (vpn_password, token)

    if DEBUG:
        print "VPN Passwd: %s" % vpn_password
        print "Google key: %s" % google_key
        print "Google OTP: %s" % token

    write_keychain_item(keychain_service, 'password', new_pass)

    if DEBUG:
        keychain_pass = get_keychain_item(keychain_service, 'password')
        print "Final pass: %s" % keychain_pass

    if NOVPN == 0:
        launch_vpn(NAME)

    if SETUP:
        print '''
    ** SECURITY NOTICE **

Note that data stored in keychain will be readable by the command-line
  application "security" without a password, provided the login keychain
  is unlocked. An attacker with access to a logged-in terminal session for
  the user who configured this may be able to extract login credentials.

To mitigate this, after setup, examine the "auth-data" and "password"
  entries for the Tunnelblick connection inside the Keychain Access 
  application. Delete the "security" application from the "always allow 
  access" list and check "Confirm + Ask for password" to force the user 
  to enter their keychain (login) password.

The "username" and "password" entries may have Tunnelblick configured for
  "always allow access."

'''



#
# ----------------------------------------------------------------
#
        
def parse_opts():
    global NOVPN, SETUP, DEBUG, NAME, OTP

    try:
        opts, args = getopt(sys.argv[1:], '', ['setup', 'no-vpn', 'debug', 'name=', 'otp=', 'help'])
    except GetoptError as err:
        print str(err)
        usage()
        sys.exit(1)

    for opt, value in opts:
        if opt == '--no-vpn':
            NOVPN = 1

        elif opt == '--setup':
            SETUP = 1

        elif opt == '--debug':
            DEBUG = 1

        elif opt == '--name':
            NAME = value

        elif opt == '--otp':
            OTP = value

        elif opt == '--help':
            usage()
            sys.exit(1)

    if NAME == '':     # we need to at least know which connection to use
        usage()
        sys.exit(1)

#
# ----------------------------------------------------------------
#

def usage():
    print '''
Options:
  --name <x> - Name of Tunnelblick vpn ("MyVPN.tblick" -> "MyVPN")
  --otp <x>  - Current Google authenticator OTP tokencode

  --no-vpn   - Don't launch Tunnelblick 
  --debug    - Show sensitive data as it's being read / generated

  --setup    - Prompt user for password and Google Auth key

Must provide at least the name (or define the name in the script).
'''

#
# ----------------------------------------------------------------
#

def get_keychain_item(service, account):
    secret = ''
    cmd = ['/usr/bin/security', 'find-generic-password', '-gs', service,
        '-a', account] 

    sub_proc = subprocess.Popen(cmd, shell=False, 
        stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    for line in sub_proc.stderr:
        if 'password:' in line:
            secret = line[11:-2]

    return secret

#
# ----------------------------------------------------------------
#

def write_keychain_item(service, account, secret):
    cmd = ["/usr/bin/security", "add-generic-password", "-U", "-s", service,
        "-a", account, "-w", secret]

    subprocess.call(cmd, shell=False)

#
# ----------------------------------------------------------------
#


def launch_vpn(name):
    sub_proc = subprocess.Popen('/usr/bin/osascript', shell=False, 
        stdout=subprocess.PIPE, stderr = subprocess.PIPE,
        stdin=subprocess.PIPE)

    cmd = 'tell app "Tunnelblick" to connect "%s"\n' % name

    sub_proc.communicate(cmd)


#
# ----------------------------------------------------------------
#

def run_setup():
    global OTP

#    
# first, see if Tunnelblick has been setup
#
    userid = get_keychain_item(keychain_service, 'username')
    password = get_keychain_item(keychain_service, 'password')

    if userid == '' or password == '':
        print "\n** ERROR **\n"
        print "You need to setup Tunnelblick to store username and password in keychain."
        print "Do this through the Tunnelblick GUI."
        print "You can verify they've been saved in the Keychain Access app."
        print "Look for items under %s" % keychain_service
        print ""
        print "Once that's done, run this setup again."

        sys.exit(1)

#
# get the user's base password 
#
    print "Enter your base VPN password (the part before the OTP token)"
    print "--> ",
    passwd = sys.stdin.readline().strip()
    print "Password entered: '%s'" % passwd
    print "Right? (Y or y to accept) --> ",
    valid = sys.stdin.readline().strip().upper()

    if valid != 'Y':
        print "Okay, then, I quit."
        sys.exit(1)

#
# collect the google authenticator key
#
    print "\nNow, open your phone (or wherever) and launch Google Authenticator.\nKeep it handy.\n"

    print "Enter your Google Authenticator key (spaces are okay)"
    print "If you'd prefer not to retain the auth key, enter 'none'"
    print "  (and you'll be prompted for a token code each time you run the script)."
    print "--> ",
    google_key = sys.stdin.readline().strip().upper()
    google_key = re.sub(' ', '', google_key)
    if google_key != 'NONE':
        print "Key entered: '%s'" % google_key
        print "Right? (Y or y to accept) --> ",
        valid = sys.stdin.readline().strip().upper()

        if valid != 'Y':
            print "Okay, then, I quit."
            sys.exit(1)

    # my google auth key was 22 letters long. it didn't b32 decode properly
    # until I paddded it with 6 As at the end. So let's try up to 8 As just
    # to be sure.
        else:
            key_valid = 0
            i = 0
            while (not key_valid) and (i < 8):
                try:
                    key = base64.b32decode(google_key)
                    key_valid = 1

                except:
                    google_key += 'A'
                    i += 1
                    print "Failed to decode. Addding an 'A' for padding."
                    print "  New key: %s" % google_key

        
            if not key_valid:
                print "Couldn't decode the google key properly."
                sys.exit(1)

            
            else:
                token = get_totp_token(google_key)
                print "Does your 'Official' Google Authenticator show this token?"
                print "  (keep in mind that this computer and your Auth device may be a few seconds off)"
                print "   --  %s --" % token

                print "(Y or y to accept) --> ", 

                valid = sys.stdin.readline().strip().upper()

                if valid != 'Y':
                    print "Okay, then, I quit."
                    sys.exit(1)

                else:
                    print "Looks like it worked!"
#
# alternatively: don't store the google code and just expect
# the user to supply a current tokencode on the command line
    else:
        print "Google Authenticator code not stored."
        print "Use --otp <token> to add current auth token when launching VPN."
        OTP = 'NONE'


#
# write it to the keychain
#
    auth_data = '%s:%s' % (google_key, passwd)
    write_keychain_item(keychain_service, 'auth-data', auth_data)


    print "\nSetup complete."

#
# ----------------------------------------------------------------
#

# OTP code adapted from https://github.com/tadeck/onetimepass
#
# We don't need the flexibility that the library offers, and
#   this way we don't have a dependency on outside code.
#
# Plus, it's cool to see how the TOTP works. :)
#
# needs: hmac, struct, time, base64, hashlib

def get_totp_token(key_str):
    key = base64.b32decode(key_str)       # the authentication key
    num = int(time.time()) // 30          # epoch time to 30 sec
    msg = struct.pack('>Q', num)          # pack into a binary thing

  # take a SHA1 HMAC of key and binary-packed time value
    digest = hmac.new(key, msg, hashlib.sha1).digest()

  # last 4 bits of the digest tells us which 4 bytes to use
    offset = ord(digest[19]) & 15
    token_base = digest[offset : offset+4]

  # unpack that into an integer and strip it down
    token_val = struct.unpack('>I', token_base)[0] & 0x7fffffff
    token = token_val % 1000000
    
    return "%06d" % token                 # pad with leading zeroes 
    
#
# ----------------------------------------------------------------
#

if __name__ == '__main__':
    main()

#
# ----------------------------------------------------------------
#

