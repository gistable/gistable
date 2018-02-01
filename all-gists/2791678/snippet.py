#!/usr/bin/env python

# Validate an IP address without using regular expression
def is_valid_ip(ip):
    if len(filter(lambda x: x.isdigit() and 0 <= int(x) <= 255, ip.split('.'))) == 4:
        return True
    return False

# Colored messages on terminal
def red(msg):#{{{
    return "\033[0;31m%s\033[0m" % msg

def blue(msg):
    return "\033[0;34m%s\033[0m" % msg

def green(msg):
    return "\033[0;32m%s\033[0m" % msg#}}}

# Validate email address
def is_valid_email(email):
    import re
    if re.compile('^[^@\ ]+@([A-Za-z0-9]+.){1,3}[A-Za-z]{2,6}$').match(email):
        return True
    return False

# Check if a user exists on system
def is_valid_user(user):
    import pwd
    try:
        pwd.getpwnam(user)
        return True
    except:
        return False

