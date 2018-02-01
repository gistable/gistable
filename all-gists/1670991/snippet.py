from __future__ import print_function
from ofxparse import OfxParser
import os
import re
import sys

if len(sys.argv) != 1:
    print ('This utility does not take command-line arguments')
    exit()

if not 'LEDGER_FILE' in os.environ:
    print ('Please set the environment variable LEDGER_FILE to point to the ledger file')
    exit()

known_ids = set()
already_imported = set()
account_id_to_account_name = {}

with open(os.environ['LEDGER_FILE'],'r') as ledger_scan:
    for line in ledger_scan:
        id_match = re.search("@id +(\S+.*)", line)
        import_match = re.search("@imported +(\S+.*)", line)
        account_map_match = re.search("@account +(\S*) +(\S+.*)", line)
        
        if id_match != None:
            known_ids.add(id_match.group(1))
        if import_match != None:
            already_imported.add(import_match.group(1))
        elif account_map_match != None:
            account_id_to_account_name[account_map_match.group(1)] = account_map_match.group(2)
        
with open(os.environ['LEDGER_FILE'],'ab') as ledger_output:
    for (dirpath,dirnames,filenames) in os.walk('.',False):
        for filename in filenames:
            if (filename.endswith('.ofx') or filename.endswith('.qfx')) and not filename in already_imported:
                print ("Importing {0}".format(filename),end='')
                with open(os.path.join(dirpath, filename),'r') as ofx_file:
                    ofx = OfxParser.parse(ofx_file)
                    account_name = account_id_to_account_name[ofx.account.number.encode('ascii')]
                    print (" ({0})".format(account_name))

                    ledger_output.write('\n\n\n\n\n;;;; ######################################################################\n')
                    ledger_output.write(';;;; @imported {0}\n'.format(filename))
                    ledger_output.write(';;;; ######################################################################\n\n')

                    def transaction_sort_key(t):
                        try:
                            return (t.date, t.payee)
                        except AttributeError:
                            return (t.date, "UNSPECIFIED PAYEE")

                    for t in sorted(ofx.account.statement.transactions, key=transaction_sort_key):
                        if len(t.id) > 10:
                            unique_id = t.id
                        else:
                            unique_id = ofx.account.number.encode('ascii') + "." + t.id
                            
                        if unique_id in known_ids:
                            continue

                        print ("    {0}".format(unique_id))
                        date = t.date.date()
                        ledger_output.write ('; @id {0}\n'.format(unique_id))

                        try:
                            payee = t.payee
                        except AttributeError:
                            payee = "UNSPECIFIED PAYEE"

                        ledger_output.write ('{0}/{1}/{2} {3}\n'.format(date.year,date.month,date.day,payee))

                        t.amount = float(t.amount)
                        if len(t.memo) > 0:
                            ledger_output.write ('    {0}    ${1:0.2f}   ; {2}\n'.format(
                                account_name, t.amount, t.memo))
                            ledger_output.write ('    Expenses:unknown\n\n')
                        else:
                            ledger_output.write ('    {0}    ${1:0.2f}\n'.format(
                                account_name, t.amount))
                            ledger_output.write ('    Expenses:unknown\n\n')
