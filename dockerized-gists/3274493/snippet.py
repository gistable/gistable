#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Armin Scrinzi, August 4, 2012
Frédéric Grosshans, 19 January 2012
Nathan R. Yergler, 6 June 2010

This file does not contain sufficient creative expression to invoke
assertion of copyright. No warranty is expressed or implied; use at
your own risk.

---

Recursively descends into a KMail maildir directory and recreates in mbox format

USAGE:
> chmod u+x 
> kmaildir_to_mbox_sub.py KMAIL_DIR MBOX_DIR

[KMAIL_DIR] path to the kmail directory
[MBOX_DIR]  directory where mbox files and subdirectories will be created

Uses Python's included mailbox library to convert mail archives from
maildir [http://en.wikipedia.org/wiki/Maildir] to
mbox [http://en.wikipedia.org/wiki/Mbox] format, icluding subfolder.

See http://docs.python.org/library/mailbox.html#mailbox.Mailbox for
full documentation on this library.

"""

import mailbox
import sys
import email
import os

def maildir2mailbox(maildirname, mboxfilename):
   """
   slightly adapted from maildir2mbox.py,
   Nathan R. Yergler, 6 June 2010
   http://yergler.net/blog/2010/06/06/batteries-included-or-maildir-to-mbox-again/


   """
   # open the existing maildir and the target mbox file
   maildir = mailbox.Maildir(maildirname, email.message_from_file)
   mbox = mailbox.mbox(mboxfilename)

   # lock the mbox
   mbox.lock()

   # iterate over messages in the maildir and add to the mbox
   for msg in maildir:
       mbox.add(msg)

   # close and unlock
   mbox.close()
   maildir.close()

def excluded(dn):
   # which directories NOT to consider
   return dn in ['new','cur','tmp'] or dn.find('.')==0 or dn.find('.sbd')!=-1 

def kmailsub(kmdir,folder):
   # how my kmail subdirectories are constructed
   return kmdir+'/.'+folder+'.directory'

def kmail_to_mbsub(kmdir,mbdir):
   """convert maildir folders in kmdir into mbox files in directory mbdir
   recursively apply to all .FOLDERNAME.directory and create corresponding .sbd 
   """  

   print(kmdir +' -> ' +mbdir)
   listofdirs=[dn for dn in os.walk(kmdir).next()[1] if not excluded(dn)]

   for curfold in listofdirs:       

      # recursively do subdirectories (if any)
      km_sub=kmailsub(kmdir,curfold)
      if os.path.exists(km_sub):
         print '\n SUBDIR: ',km_sub
         mb_sbd=mbdir+'/'+curfold+'.sbd'
         if not os.path.exists(mb_sbd): 
            os.makedirs(mb_sbd)
         kmail_to_mbsub(km_sub,mb_sbd)
         print '--- subdirectory done --\n'

      # convert current maildir 
      maildir=kmdir+'/'+curfold
      mbname =mbdir+'/'+curfold

      # skip if does not contain 'cur'
      if 'cur' not in os.walk(maildir).next()[1]: continue
      print 'CONVERT: ',maildir+' -> '+mbname
      maildir2mailbox(kmdir+'/'+curfold,mbdir+'/'+curfold)


if __name__ == "__main__":
   kmail=sys.argv[-2]
   mbname=sys.argv[-1]
   kmail_to_mbsub(kmail,mbname)

   print('Done')
