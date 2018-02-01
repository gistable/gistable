#!/usr/bin/env python

import csv
import collections
import re
import json

import requests


IMDB_URL = "http://www.imdb.com/list/export?list_id=watchlist&author_id={imdb_user}"
TRAKT_API = "http://api.trakt.tv/movie/watchlist/{apikey}"


def stream_imdb(username='username'):
    type_name = re.compile(r'[^a-zA-Z0-9_]')
    first_letter = re.compile(r'[^a-zA-Z]')
    def to_python_var(s):
        header_name = type_name.sub('_', s).lower()
        while first_letter.match(header_name[0]):
            header_name = header_name[1:]
        return header_name


    url = IMDB_URL.format(imdb_user=username)

    r = requests.get(url)
    r.raise_for_status()

    reader = csv.reader(r.iter_lines())
    headers = [to_python_var(s) for s in next(reader)]
    model = collections.namedtuple('IMDb', headers)

    for line in reader:
        yield model(*line)

def post_trakt(movies, username='username', password='password', apikey='apikey'):
    def make_movie(model):
        data = {
            "imdb_id": model.const,
            "title": model.title
        }
        if '?' not in model.year:
            data['year'] = model.year

        return data

    payload = {
        "movies"  : [ make_movie(m) for m in movies ]
    }

    url = TRAKT_API.format(apikey=apikey)

    r = requests.post(url, data=json.dumps(payload), auth=(username, password))
    r.raise_for_status()

    return r

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--imdb-user', required=True)
    parser.add_argument('-u', '--trakt-user', required=True)
    parser.add_argument('-p', '--trakt-pass', required=True)
    parser.add_argument('-a', '--trakt-apikey', required=True)

    arguments = parser.parse_args()

    print post_trakt(
        stream_imdb(arguments.imdb_user),
        arguments.trakt_user,
        arguments.trakt_pass,
        arguments.trakt_apikey,
    ).text

