#!/usr/bin/env python
#
# Checks the Azure AD Connect status in Office 365
#
# The user used to check the Azure AD Connect status needs to be an Administrator of some sort
#
# Setup:
#  pip install mechanize
#
# Usage:
#   ./check_aad_sync_status.py -u username -p pasword
#   ./check_aad_sync_status.py -F /path/to/file.cred
# 
# Cred File format:
#   username = username
#   password = password
#
# It is recommended that you set your credential file to 600 (`chmod 600 /path/to/file.cred`) to
# help prevent the credentials from being leaked.
#
# :author David Lundgren <dlundgren@syberisle.net>:
# :author Sylvain Guibert (updated documentation):

import sys
import ConfigParser
import StringIO
import json
import optparse
import mechanize
from time import sleep
import os

def find_form_by_id(browser, id):
    i = 0
    for form in browser.forms():
        if str(form.attrs["id"]) == id:
            break
        i = i + 1
    return i


def main():
    parser = optparse.OptionParser()
    parser.add_option("-u", dest="user", help="Username (with access to admin)")
    parser.add_option("-p", dest="password", help="Password")
    parser.add_option("-F", dest="credfile", help="Credential file")

    options, args = parser.parse_args()

    if options.credfile is not None:
        credfile = '[root]\n' + open(options.credfile, 'r').read()
        config = ConfigParser.SafeConfigParser()
        config.readfp(StringIO.StringIO(credfile))
        username = config.get('root', 'username')
        password = config.get('root', 'password')
    elif options.user is not None and options.password is not None:
        username = options.user
        password = options.password
    else:
        print "Missing user information"
        sys.exit(1)

    b = mechanize.Browser()
    b.set_handle_robots(False)
    b.set_handle_refresh(False)
    b.addheaders =[
        ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')
    ]

    # LOGIN
    b.open('https://portal.office.com/Home')
    b.select_form(nr=find_form_by_id(b, 'credentials'))
    b.set_all_readonly(False)

    b['login'] = username
    b['passwd'] = password
    b.submit()
    sleep(1)

    try:
        b.select_form(name='fmHF')
    except mechanize._mechanize.FormNotFoundError, e:
        print "AAD_SYNC UNKNOWN - Unable to login"
        os._exit(3)

    b.submit()
    sleep(2)

    # GET the dirsync data
    b.addheaders = [
        ('Accept', 'application/json, text/plain, */*'),
        ('x-adminapp-request', '1'),
        ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'),
        ('Referer', 'https://portal.office.com/AdminPortal/Home')
    ]
    data = json.loads(b.open('https://portal.office.com/admin/api/DirSyncManagement/manage').read())

    status = 'OK'
    # DirSync status
    ds_status = None
    if data['IsDirSyncEnabled'] is True:
        ds_status = 'OK'
        if data['IsDirSyncObjectErrors'] is True or data['IsDirSyncRedWarning'] is True:
            status = 'CRITICAL'
            ds_status = 'CRITICAL'


    ps_status = None
    if data['IsPasswordSyncEnabled'] is True:
        ps_status = 'OK'
        if data['IsPasswordSyncNormal'] is False:
            if status is 'OK':
                status = 'WARNING'
            ps_status = 'WARNNING'
        if data['IsPasswordSyncRedWarning'] is True:
            if status is 'OK':
                status = 'CRITICAL'
            ps_status = 'CRITICAL'


    print "AAD_SYNC %s -" % status,
    if not ds_status is None:
        print "DirSync %s," % ds_status,
    if not ps_status is None:
        print "PasswordSync %s" % ps_status

    if status is "WARNING":
        os._exit(1)

    if status is "CRITICAL":
        os._exit(2)


if __name__ == "__main__":
    main()
