#!/usr/bin/env python3

import argparse
import csv
import requests
import sys

from getpass import getpass

def do_login(session, username, password):
    if password is None:
        password = getpass()
    r = session.post('https://www.duolingo.com/login', params={'login': username, 'password': password})
    if r.status_code != 200:
        raise Exception('Duolingo returned status code {} when logging in'.format(r.status_code))
    elif 'failure' in r.json():
        raise Exception('Invalid credentials')

def set_language(session, language):
    r = session.post('https://www.duolingo.com/switch_language', params={'learning_language': language})
    if r.status_code != 200:
        raise Exception('Duolingo returned status code {} when setting language'.format(r.status_code))

def get_words(session):
    r = session.get('https://www.duolingo.com/vocabulary/overview')
    if r.status_code != 200:
        raise Exception('Duolingo returned status code {} when getting word list'.format(r.status_code))
    j = r.json()

    for w in j['vocab_overview']:
        if w['normalized_string'] == '<*sf>':
            continue
        yield {'Word': w['word_string'], 'Strength': w['strength']}

def output_csv(words):
    writer = csv.DictWriter(sys.stdout, fieldnames=['Word', 'Strength'])
    writer.writeheader()
    for w in words:
        writer.writerow(w)

def main(args):
    session = requests.Session()

    try:
        do_login(session, args.username, args.password)
        set_language(session, args.language)
        words = get_words(session)
        output_csv(words)
    except Exception as e:
        print("Error: {}".format(str(e)), file=sys.stderr)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Gets a word list from Duolingo and outputs it in CSV format')
    parser.add_argument('--username', '-u', help='Username', required=True)
    parser.add_argument('--password', '-p', help='Password')
    parser.add_argument('--language', '-l', help='Language', required=True)

    args = parser.parse_args();

    main(args)