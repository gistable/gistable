#! /usr/bin/python

import optparse

def main(options):
    '''
    Performs the amazingly useful tasks for this command line tool
    '''
    pass

def verifyUserInput(options):
    '''
    Raises errors if options passed on command line are invalid
    '''
    
    # Test the options. This example is silly and wouldn't happen IRL.
    if type(options.filename) != type(''):
        raise TypeError("Filename must be a string")

if __name__ == '__main__':
    # Create a parser for command line arguments
    parser = optparse.OptionParser()
    
    # Add options as needed for this tool
    parser.add_option("-f", "--file", dest="filename",
                      help="write report to FILE", metavar="FILE")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")

    (options, args) = parser.parse_args()
    
    # Check for malformed or invalid inputs
    verifyUserInput(options)
    
    main(options)