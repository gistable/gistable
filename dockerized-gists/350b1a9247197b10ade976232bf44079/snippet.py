# delete  599 and 910 fields from a current directory full of individual mrc files
# (python 3 script)
# pymarc:  https://github.com/edsu/pymarc
# help found at https://gist.github.com/symac/0133cae8846c134e849c and https://gist.github.com/EG5h/0ac510047f39e0cf930a

import os
import glob
import pymarc
errorlist = ""
path = os.path.dirname(os.path.abspath(__file__)) + '\\'
for infile in glob.glob( os.path.join(path, '*.mrc') ):
        with open(infile, 'rb') as fh:
                reader = pymarc.MARCReader(fh, force_utf8=True)
                record = next(reader)
                new_record = pymarc.Record(to_unicode=True, force_utf8=True)
                new_record.leader = record.leader
                for field in record.get_fields():
                        new_record.add_field(field)
                for f in new_record.get_fields('599'):
                        new_record.remove_field(new_record.get_fields('599')[0]) # only grabs first instance of 599 but only rarely will there be more than one
                        print ("deleted 599 from " + infile)
                for f in new_record.get_fields('910'):
                        new_record.remove_field(new_record.get_fields('910')[0]) # some old records have 910 for stats
                        print ("deleted 910 from " + infile)

                out = pymarc.MARCWriter(open(infile, 'wb'))
# the MARCWriter part above can be modified to create xml, json, and mnemonic mrk formats instead
                try:
                        out.write(new_record)
                except Exception:
                        errorlist += infile + '\n' 
                        
                out.close()
if errorlist != "":
        with open(path + 'errors.log', 'w+') as fh:
                fh.write(errorlist)