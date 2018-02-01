#!/usr/bin/python

''' Python command line argument example using argparse module

Example output:

./parser.py --server=pyserver --port=8080,443,25,22,21 --keyword=pyisgood

Server name: [ pyserver ]

Port: [ 8080 ]
Port: [ 443 ]
Port: [ 25 ]
Port: [ 22 ]
Port: [ 21 ]

Keyword assigned: [ pyisgood ]

'''

import argparse

__author__ = 'Jason Vasquez Orona'


def get_args():
    '''This function parses and return arguments passed in'''
    # Assign description to the help doc
    parser = argparse.ArgumentParser(
        description='Script retrieves schedules from a given server')
    # Add arguments
    parser.add_argument(
        '-s', '--server', type=str, help='Server name', required=True)
    parser.add_argument(
        '-p', '--port', type=str, help='Port number', required=True, nargs='+')
    parser.add_argument(
        '-k', '--keyword', type=str, help='Keyword search', required=False, default=None)
    # Array for all arguments passed to script
    args = parser.parse_args()
    # Assign args to variables
    server = args.server
    port = args.port[0].split(",")
    keyword = args.keyword
    # Return all variable values
    return server, port, keyword

# Run get_args()
# get_args()

# Match return values from get_arguments()
# and assign to their respective variables
server, port, keyword = get_args()

# Print the values
print "\nServer name: [ %s ]\n" % server

for p in port:
    print "Port: [ %s ]" % p

print "\nKeyword assigned: [ %s ]\n" % keyword
