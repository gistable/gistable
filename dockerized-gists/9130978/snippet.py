#!/usr/bin/python -tt
#     __                                           _             __   _    
#    / /_  __  __   ______________ _____  __  __  (_)_  ______  / /__(_)__ 
#   / __ \/ / / /  / ___/ ___/ __ `/_  / / / / / / / / / / __ \/ //_/ / _ \
#  / /_/ / /_/ /  / /__/ /  / /_/ / / /_/ /_/ / / / /_/ / / / / ,< / /  __/
# /_.___/\__, /   \___/_/   \__,_/ /___/\__, /_/ /\__,_/_/ /_/_/|_/_/\___/ 
#       /____/                         /____/___/                          
#
###############################################################################
# Download huge collections of wordlist:#
#http://ul.to/folder/j7gmyz#
##########################################################################
#
####################################################################
# Need daylie updated proxies?#
#http://j.mp/Y7ZZq9#
################################################################
#
######################################################
#### whois client ######
###################################################
#
# Attempt at writing a simple python whois client

import sys
import socket

def whois(domain, server, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((server,port))
    except IOError, err:
        print "Unable to connect to %s port %d:\n%s" % (server, port, err)
        exit(1)

    s.send(domain+'\n')

    result = ''
    while True:
        str = s.recv(1024)
        if not str:
            break
        else:
            result += str

    s.close()
    return result

def errexit(str):
    print str
    sys.exit(1)

def main():
    server = 'whois.verisign-grs.com'
    port = 43

    if sys.argv:
        program = sys.argv.pop(0)
    if sys.argv:
        domain = sys.argv.pop(0)
    else:
        print "syntax: mywhois <domain> (<server>)"
        sys.exit(1)        
    if sys.argv:
        server = sys.argv.pop(0)
    
    print "WHOIS Lookup on Domain %s on Server %s:%d" % (domain,server,port)
    output = whois(domain,server,port)
    print output
    
if __name__ == '__main__':
    main()