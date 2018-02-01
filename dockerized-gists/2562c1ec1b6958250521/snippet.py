#!/usr/bin/env python
"""Sample the modem's signal

This script is meant to be run with the Motorola SB6121 Surfboard Modem.

If you run it on a different modem, it might not work, but it's worth a try...

It should be run as a cron job, every minute (or whatever interval you'd like)
into a text file. The file can later be used by a json parser to analyze the
signal over time, which can be used to come to conclusions that you can argue
with the cable company's tech support about when the service goes down.""" 

import sys
import os
from optparse import OptionParser
import fileinput
import logging

from collections import namedtuple
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

# Default paramaters to be used by option parser
DEFAULT_SIGNAL_URL = "http://192.168.100.1/cmSignalData.htm"

# Set up logging
log = logging.getLogger(__name__)
hdlr = logging.StreamHandler()
log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(log_formatter)
log.addHandler(hdlr) 


def set_log_level(verbosity):
    """ 
    Set the log level based on an integer between 0 and 2
    """ 

    log_level = logging.WARNING # default
    if verbosity == 1:
        log_level = logging.INFO
    elif verbosity >= 2:
        log_level = logging.DEBUG

    log.setLevel(level=log_level)

def get_options():
    """ 
    Returns the options and arguments passed to this script on the commandline

    @return: (options,args)
    """ 

    usage = "usage: %prog [options] file1 file2 ..." 
    parser = OptionParser(usage)

    parser.add_option("-u", "--signal-url", dest="signal_url", default=DEFAULT_SIGNAL_URL,
                      help="The signal url Default: [default: %default]")
    parser.add_option('-v', '--verbose', dest='verbose', action='count',
                      help="Increase verbosity (specify multiple times for more)")

    options, args = parser.parse_args()

    return (options, args)

def main(args):
    (options, args) = get_options()
    set_log_level(options.verbose)

    log.debug("Starting with options: %s" % (options))
    
    
    timestamp = datetime.now().isoformat()
    
    try:
        r = requests.get(options.signal_url)
        soup = BeautifulSoup(r.content, 'html.parser')
    except:
        print json.dumps({'timestamp':timestamp, 'res':"error"})
        return
    
    res = {}
    
    for table in soup.find_all("table"):
        if not table.th:
            continue
        
        heading = table.th.font.contents[0]
        
        res[heading] = {}
        
        if heading:
            for table_row in table.find_all("tr"):
                if table_row.th:
                    continue
                
                row_data = []
                
                for s in table_row.stripped_strings:
                    if s.startswith("The Downstream Power Level reading is a"):
                        continue
                    
                    row_data.append(s)
                
                if row_data:
                    res[heading][row_data[0]] = row_data[1:]
    
    print json.dumps({'timestamp':timestamp, 'res':res})
    
    
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))