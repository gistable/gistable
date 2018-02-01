#!/usr/bin/python2.7

import sys

def gftp_descrable_password(password):
    """gftp password descrambler

    This code has been released in the Public Domain by the original author.

    """
    if not password.startswith('$'):
        return password
    newpassword = []
    pwdparts = map(ord, password)
    for i in range(1, len(pwdparts), 2):
        if ((pwdparts[i] & 0xc3) != 0x41 or
            (pwdparts[i+1] & 0xc3) != 0x41):
            return password
        newpassword.append(chr(((pwdparts[i] & 0x3c) << 2) +
                               ((pwdparts[i+1] & 0x3c) >> 2)))
    return "".join(newpassword)


def main(argv):
    sys.stdout.write("password: %s\n" % gftp_descrable_password(sys.argv[1]))

if __name__ == "__main__":
    main(sys.argv[1:])
