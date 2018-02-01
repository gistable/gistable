#!/usr/bin/env python

from smtplib import SMTP, SMTP_SSL
from poplib import POP3, POP3_SSL
from imaplib import IMAP4, IMAP4_SSL
import argparse


def smtp(host, user, password):
    tests = [SMTP(host), SMTP_SSL(host)]
    for test in tests:
        test.set_debuglevel(True)
        test.login(user, password)


def pop3(host, user, password):
    tests = [POP3(host), POP3_SSL(host)]
    for test in tests:
        test.set_debuglevel(1)
        test.user(user)
        test.pass_(password)
        test.quit()


def imap4(host, user, password):
    tests = [IMAP4(host), IMAP4_SSL(host)]
    for test in tests:
        test.debug = 3
        test.login(user, password)
        test.noop()
        test.logout()


def main():
    p = argparse.ArgumentParser(description='test smtp/pop3/imap4 auth')
    p.add_argument('host', type=str, metavar='<host>')
    p.add_argument('username', type=str, metavar='<username>')
    p.add_argument('password', type=str, metavar='<password>')
    args = p.parse_args()
    tests = [smtp, pop3, imap4]
    for test in tests:
        test(args.host, args.username, args.password)


if __name__ == '__main__':
    main()
