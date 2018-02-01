#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) Ruoyan Wong
#
# MailAnalysis - main.py
#

import email, imaplib


def get_email_addressee(_email_instance):

    _addressee = email.Header.decode_header(_email_instance['to'])

    encoding_addressee = _addressee[0][0]
    encoding = _addressee[0][1]

    if encoding is not None:
        addressee = unicode(encoding_addressee, encoding)
    else:
        addressee = encoding_addressee

    return addressee


def get_email_subject(_email_instance):

    _subject = email.Header.decode_header(_email_instance['subject'])

    encoding_subject = _subject[0][0]
    encoding = _subject[0][1]

    if encoding is not None:
        subject = unicode(encoding_subject, encoding)
    else:
        subject = encoding_subject

    return subject


def get_email_body(_email_instance):

    if _email_instance.is_multipart():
        for single_email in _email_instance.walk():

            if single_email.get_content_maintype() == 'text':
                email_content_charset = single_email.get_content_charset()
                if email_content_charset == 'None':
                    return single_email.get_payload()
                else:
                    try:
                        return unicode(single_email.get_payload(decode=True), email_content_charset)
                    except Exception,e:
                        return 'None'
    else:
        if _email_instance.get_content_maintype() == 'text':
            email_content_charset = _email_instance.get_content_charset()
            if email_content_charset == 'None':
                return _email_instance.get_payload()
            else:
                try:
                    return unicode(_email_instance.get_payload(decode=True), email_content_charset)
                except Exception,e:
                    return 'None'


if __name__ == '__main__':

    M = imaplib.IMAP4_SSL('imap.163.com', 993)
    M.login('username', 'password')

    M.select('INBOX')

    # t, data = M.search(None, '(UNSEEN)')
    t, data = M.search(None, 'ALL')

    for sequence_number in data[0].split():
        t, data = M.fetch(sequence_number, '(RFC822)')
        email_instance = email.message_from_string(data[0][1])

        email_to = get_email_addressee(email_instance)
        email_body = get_email_body(email_instance)
        email_subject = get_email_subject(email_instance)

        print('To: %s ' % email_to)
        print('Subject: %s ' % email_subject)
        print('Body: %s ' % email_body)


    M.close()
    M.logout()