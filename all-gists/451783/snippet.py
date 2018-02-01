# encoding: utf-8

""" Python General Helpers
     Copyright (c) 2010 Kenneth Reitz. Creative Commons Attribution 3.0 License.
"""

import urllib, re, time, sys
import paramiko


class Object(object):
    """Your attributes are belong to us."""

    def __init__(self, **entries): 
        self.__dict__.update(entries)
    def __getitem__(self, key):
        return getattr(self, key)



def iscollection(obj): 
    """Tests if an object is a collection"""
    
    col = getattr(obj, '__getitem__', False) 
    val = False if (not col) else True

    if isstring(obj):
        val = False
    
    return val


def isstring(obj):
    """Tests if an object is a string"""
    
    return True if type(obj).__name__ == 'str' else False

def print_args(function):
     def wrapper(*args, **kwargs):
         print 'Arguments:', args, kwargs
         return function(*args, **kwargs)
     return wrapper


def enc(str):
    """Encodes a string to ascii"""

    return str.encode('ascii', 'ignore')


def dec(str):
    """Decodes a string to ascii"""

    return str.decode('ascii', 'ignore')


def get_file(path):
    """Returns a file as a string"""

    return open(path, 'r').read()


def get_file_lines(path):
    """Returns a file as a list of strings"""

    return open(path, 'r').readlines()


def get_http(uri):
    """Fetches a file over http as a string"""

    return urllib.urlopen(uri).read()


def get_http_lines(uri):
    """Fetches a file over http as a file object"""

    return urllib.urlopen(uri).readlines()


def get_sftp(hostname, username, password, filename):
    """Fetches a file over sftp as a string
        Note: Server must be in known_hosts.
    """

    client = paramiko.SSHClient()
    print("Download of %s started" % filename)
    client.load_host_keys('/root/.ssh/known_hosts')
    client.connect(hostname=hostname, username=username, password=password)
    file = client.open_sftp().open(filename).read()
    print("Download of %s complete" % filename)

    return file

def get_piped():
    """Returns piped input via stdin, else False"""
    
    with sys.stdin as stdin:
        return stdin.read() if not stdin.isatty() else None
