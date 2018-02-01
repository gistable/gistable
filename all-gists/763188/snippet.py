#!/usr/bin/env python

import getpass, mechanize, optparse, os.path, sys

parser = optparse.OptionParser()
parser.add_option('--login')
parser.add_option('--password')
parser.add_option('--filename')
parser.add_option('--description')
parser.add_option('--private', action='store_true', default=False)
(options, args) = parser.parse_args()

br = mechanize.Browser()

if options.login:
    if not options.password:
        options.password = getpass.getpass('Password for %s@github: ' % options.login)

    br.open('https://gist.github.com/login')
    br.select_form(nr=1)
    br.form.find_control('login').value = options.login
    br.form.find_control('password').value = options.password
    result = br.submit()

br.open('https://gist.github.com')
br.select_form(nr=1)
br.form.find_control('file_contents[gistfile1]').value = sys.stdin.read()

if options.filename:
    br.form.find_control('file_name[gistfile1]').value = options.filename
if options.description:
    br.form.find_control('description').value = options.description
if options.private:
    br.submit(nr=0)
else:
    br.submit(nr=1)

print br.geturl()

if os.path.exists('/usr/bin/pbcopy'):
    retval = os.system('echo %r | /usr/bin/pbcopy' % br.geturl())
    if retval == 0:
        print 'Copied gist url (%s) to the clipboard.' % br.geturl()