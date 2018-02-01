#!/usr/bin/python

# ***************************************
#
# A script that finds all available single word .io domains
#
# use: python finder.py
#
# Results are saved in results.txt
#
# ***************************************

import re
import socket
import sys
import time

PORT = 43
SERVER = 'whois.nic.io'
WORD_FILE = '/usr/share/dict/words'

def whois(query):
    "Make a whois query i.e whois(mysite.io)"
    s = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
    try:
        s.connect((SERVER , PORT))
    except socket.error, msg:
        print 'Socket connection error ' + msg
        sys.exit();
    s.send(query + '\r\n')
    msg = ''
    while len(msg) < 1000:
        chunk = s.recv(100)
        if chunk == '':
            break
        msg = msg + chunk
    s.close()
    return msg

def parse_response(resp):
    "Returns boolen true if a domain is available"
    expr = r'not available'
    found = re.search(expr, resp.lower())
    if found: return False
    else: return True

def search(domain):
    result = whois(domain)
    return result.splitlines()[0]

def make_full_domain(word):
    full_domain = "%s.io" % (word)
    return full_domain.lower()

# Word length utils
# ******************************************

def word_starts_with(word, letter):
    return word[0] == letter

def word_less_than(word, bound):
    return len(word) < bound

# Save to file
# ******************************************

# Save the search result to disk
def save_result(result):
    with open("results.txt", "a") as f:
        f.write(result + '\n')

# Main
# ******************************************

def main():
    with open("/usr/share/dict/words", 'r') as file:
        for line in file:
            word = line.strip().lower()
            domain = make_full_domain(word)
            try:
                response = parse_response(search(domain))
                if response:
                    print "Found domain %s" % (domain)
                    save_result(domain)
            except: pass

if __name__ == '__main__':
    print("Searching for available .io domains...\n")
    main()

