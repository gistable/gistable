#!/usr/bin/env python
# encoding: utf-8
"""
split_ln.py

Created by Neal Caren on 2012-05-14.
neal.caren@unc.edu

Edited by Alex Hanna on 2015-01-29
alex.hanna@gmail.com

Takes a downloaded plain text LexisNexis file and converts it into a CSV file or set of flat files.

"""

import argparse, csv, os, re, sys
from datetime import datetime

parser = argparse.ArgumentParser(description='Parse Lexis-Nexis files into different outputs.')
parser.add_argument('files', metavar='file', type=str, nargs='+', help='Lexis-Nexis files to be parsed.')
parser.add_argument('--output_dir', dest='output', action='store', help='Directory in which to store the output.')
parser.add_argument('--sep', dest='sep', const='sep', default='csv', action='store_const', 
    help = 'Flag to store output in separate files.')

args = parser.parse_args()

if args.output:
    if not os.path.isdir(args.output):
        print("Not a valid directory.")
        sys.exit(-1)
else:
    args.output = "."

## set permanent columns
header = ['SEARCH_ID', 'PUBLICATION', 'DATE', 'TITLE', 'EDITION']

if args.sep == 'csv':
    ## use today as a hash to store
    today_str = datetime.today().strftime('%Y-%m-%d')
    outname   = "%s/lexis-nexis_%s.csv" % (args.output, today_str)

    # setup the output file
    outfile = open(outname,'wb')
    writer  = csv.writer(outfile)

for fn in args.files:
    print('Processing %s' % fn) 
    header_written = False

    # read the file
    lnraw = open(fn).read()

    # silly hack to find the end of the documents
    workfile = re.sub('                Copyright .*?\\r\\n','ENDOFILE',lnraw)

    # clean up crud at the beginning of the file
    workfile = workfile.replace('\xef\xbb\xbf\r\n','') 

    # split the file into a list of documents
    workfile = workfile.split('ENDOFILE') 

    # remove blank rows
    workfile = [f for f in workfile if len(f.split('\r\n\r\n')) > 2] 
    
    # Figure out what metadata is being reported
    meta_list  = list(set(re.findall('\\n([A-Z][A-Z-]*?):',lnraw))) 

    # Keep only the commonly occuring metadata
    meta_list = [m for m in meta_list if float(lnraw.count(m)) / len(workfile) > .20] 

    if args.sep == 'csv':
        header.extend(meta_list)
        header.append('TEXT')

        ## write header if this hasn't been done
        ## TK: Not sure how to deal with the case where metadata changes
        ## between different input files
        if not header_written:
            writer.writerow(header)
            header_written = True
        
    ## Begin loop over each article
    for f in workfile:
        # Split into lines, and clean up the hard returns at the end of each line.
        # Also removes blank lines that the occasional copyright lines  
        filessplit = [row.replace('\r\n', ' ').strip() for row in f.split('\r\n\r\n') if len(row) > 0 and 'All Rights Reserved' not in row]

        ## make metadata dict
        meta_dict  = {k : '' for k in header}

        doc_id  = filessplit[0].strip().split(' ')[0]
        pub     = filessplit[1].strip()
        date_ed = filessplit[2].strip()
        title   = filessplit[3].strip()

        ## format date into YYYY-MM-DD
        da   = date_ed.replace(',', '').split()
        date = datetime.strptime(" ".join(da[0:3]), "%B %d %Y")
        date = date.strftime("%Y-%m-%d")

        ## format edition
        ## TK: maybe remove?
        ed = date_ed.replace(date,'').split('                         ')[-1].lstrip()

        ## if edition is a time or day, skip it             
        if 'GMT' in ed or 'day' in ed:
            ed = ''
        
        ## Edit the text and other information
        paragraphs = []
        for line in filessplit[5:]:
            ## find out if this line is part of the main text
            if len(line) > 0 and line[:2] != '  ' and line != line.upper() and len(re.findall('^[A-Z][A-Z-]*?:',line)) == 0 and title not in line:
                ## remove new lines
                line = re.sub(r'\s+', ' ', line)

                ## not sure what this does
                line = line.replace('","','" , "')

                ## add to paragraph array
                paragraphs.append(line)
            else:
                metacheck = re.findall('^([A-Z][A-Z-]*?):', line)
                if len(metacheck) > 0:
                    if metacheck[0] in meta_list:
                       meta_dict[metacheck[0]] = line.replace(metacheck[0] + ': ','')  

        ## put everything in the metadata dictionary
        meta_dict['PUBLICATION'] = pub
        meta_dict['SEARCH_ID']  = doc_id
        meta_dict['DATE']        = date
        meta_dict['TITLE']       = title
        meta_dict['EDITION']     = ed

        if args.sep == 'csv':
            ## add the text to the dict to write
            meta_dict['TEXT'] = " ".join(paragraphs)

            # Output the results to a single csv file
            writer.writerow( [ meta_dict[x] for x in header ] )
        else:
            ## otherwise, store as separate files
            ## put each piece of meta info on a single line
            out = "%s/%s_%s.txt" % (args.output, doc_id, date)
            fh  = open(out, 'w')

            ## write title and date first for separate files
            fh.write('TITLE: %s\n' % meta_dict['TITLE'])
            fh.write('DATE: %s\n'  % meta_dict['DATE'])

            ## then write the rest
            for k,v in meta_dict.iteritems():
                if k not in ['TITLE', 'DICT']:
                    fh.write('%s: %s\n' % (k,v))

            ## write the text last
            fh.write("\n\n".join(paragraphs) + "\n")

            fh.close()
        
        print('Wrote %s' % doc_id)

if args.sep == 'csv':
    outfile.close()
