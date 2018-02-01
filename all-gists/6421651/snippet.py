#!/usr/bin/env python
#
# Require python 2.5 or higher
#
# Usage:
#     script.py <maillog> [maillog]...

import re
from os import mkdir
from sys import argv

def exception(line):
    print(line)
    raise

# parse functions
def mail_id(line):
    id = line.split(':')[3].strip()
    if len(id) == 14:
        return id
    exception(line)

def relay(line):
    r = re.compile("relay=\[?([\w@.-]+)\]?")
    result = r.search(line)
    if result is not None:
        return result.group(1)
    exception(line)

def to_addresses(line):
    # return list element. each element are one mail address.
    r = re.compile("ctladdr=<?([\w@.-]+)>?")
    result = r.search(line)
    if result is not None:
        return [result.group(1) + '\n']

    r = re.compile("to=<?(.*), delay")
    result = r.search(line)
    if result is not None:
        mailAddresses = result.group(1).split(',')
        array = []
        for i in mailAddresses:
            if i != ' [more]':
                array.append(i.strip(' <>') + '\n')
        return array
    exception(line)

# evaluate functions
def is_from_log(line):
    return True if line.find(" from=") != -1 else False

def is_to_log(line):
    return True if line.find(" to=") != -1 else False

# main
sent_to_addresses = {} # key : server name, value : list of To mail addresses.
for file in argv:
    if file == argv[0]:
        continue

    f = open(file)
    dict = {} # key : mail_id, value : relayserver
    for line in f:
        if is_from_log(line):
            dict[mail_id(line)] = relay(line)
        elif is_to_log(line):
            try:
                relayServer = dict[mail_id(line)]
            except:
                print('Invalid mail_id ' + mail_id(line))
                continue
            if relayServer not in sent_to_addresses:
                sent_to_addresses[relayServer] = []
            for addr in to_addresses(line):
                sent_to_addresses[relayServer].append(addr)
    f.close()

# output
mkdir('tolist')
for server in sent_to_addresses.keys():
    f = open('tolist/' + server + '.tolist', 'w')
    f.writelines(sorted(set(sent_to_addresses[server])))
    f.close()