r"""
vCard_S30.py -- Convert vCards into suitable for Nokia Series 30+ format, or
How to solve the only one phone number per contact problem.

1) Import contacts "contacts.vcf" from Google account (vCard format).
2) Place it beside this script.
3) Run the script with Python 2.7.
4) Copy the result "backup.dat" into "Backup" folder on the phone SD card.
5) Restore contacts from backup on the phone.

Tested on Nokia 220.

The MIT License (MIT)
Copyright (c) 2016 in4lio@gmail.com
"""

import sys
import os

CARD = """
BEGIN:VCARD
VERSION:2.1
FN:%s
TEL;VOICE;CELL:%s
END:VCARD
"""

cp  = sys.stdout.encoding if sys.stdout.encoding else 'utf8'
sou = map( str.strip, open( './contacts.vcf' ).read().splitlines())
res = open( './backup.dat', 'w' )
err = 0

for s in sou:
    if s == 'BEGIN:VCARD':
        print '{',
        fn = ''
        tel = []
        mark = 'FN:'

    elif s == 'END:VCARD':
        print '}'
        if not fn:
            print '#### ERROR: NO NAME ####'
            err += 1
        elif not tel:
            print '#### ERROR: NO PHONE ####'
            err += 1
        else:
            for i, t in enumerate( tel ):
                res.write( CARD % ( fn + ( ' %d' % i if i else '' ), t ))

    elif s.startswith( mark ):
        if len( s ) > len( mark ):
            fn = s.split( ':', 1 )[ 1 ]
            print s.decode( 'utf8' ).encode( cp, 'replace' ),
        else:
            mark = 'ORG:'

    elif s.startswith( 'TEL' ):
            tel.append( s.split( ':', 1 )[ 1 ])
            print s,

res.close()

print '#### DONE ####'
if err:
    print '%d ignored contact(s)' % err
