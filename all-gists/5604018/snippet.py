#-*-coding: utf-8-*-
"""
Simple script to dump documents out of a CouchDB database and straight into
a Couchbase instance.
"""

import time
import sys
import argparse

from hashlib import sha256
from base64 import urlsafe_b64encode

try:
    import simplejson as json
except ImportError:
    import json

import requests
from couchbase import Couchbase


def _print_error(message):
    """
    Print a message to stderr, with a newline.
    """
    sys.stderr.write(str(message) + "\n")
    sys.stderr.flush()


def _encode_key_if_necessary(key):
    """
    If a key is >250 bytes long, encode it as a SHA256 hash.

    This is necessary because Couchbase keys can't be > 250 bytes in length,
    since all the keys and metadata is kept in RAM on the cluster. CouchDB has
    no such restriction, and IDs may be very long.
    """
    if len(key) >= 250:
        return urlsafe_b64encode(sha256(key).digest())
    return key


def _all_docs_by_page(db_url, page_size=10):
    """
    Helper function to request documents from CouchDB in batches ("pages") for
    efficiency, but present them as a stream.
    """
    # Tell CouchDB we only want a page worth of documents at a time, and that
    # we want the document content as well as the metadata
    view_arguments = {'limit': page_size, 'include_docs': "true"}

    # Keep track of the last key we've seen
    last_key = None

    while True:
        response = requests.get(db_url + "/_all_docs", params=view_arguments)

        # If there's been an error, stop looping
        if response.status_code != 200:
            _print_error("Error from DB: " + str(response.content))
            break

        # Parse the results as JSON. If there's an error, stop looping
        try:
            results = json.loads(response.content)
        except:
            _print_error("Unable to parse JSON: " + str(response.content))
            break

        # If there's no more data to read, stop looping
        if 'rows' not in results or not results['rows']:
            break

        # Otherwise, keep yielding results
        for r in results['rows']:
            last_key = r['key']
            yield r

        # Update the view arguments with the last key we've seen, so that we
        # can step forward properly by page. (Of course, we actually need a key
        # that is just _after_ the last one we've seen, so tack on a high
        # Unicode character).
        # Note that CouchDB requires keys to be encoded as JSON
        last_key = last_key + u'\xff'
        view_arguments.update(startkey=json.dumps(last_key))


if __name__ == '__main__':

    # Set up an ArgumentParser to read the command-line
    parser = argparse.ArgumentParser(
        description="Dump documents out of CouchDB to the filesystem")

    parser.add_argument(
        'db', type=str,
        help="The CouchDB database URL from which to load data")

    parser.add_argument(
        "--page-size", type=int, default=1000,
        help="How many documents to request from CouchDB in each batch.")

    parser.add_argument(
        "--couchbase-host", default="127.0.0.1",
        help="The host for the Couchbase server")

    parser.add_argument(
        "--couchbase-bucket", default="default",
        help="The destination Couchbase bucket")

    parser.add_argument(
        "--couchbase-password", default="",
        help="The password for the destination bucket")

    args = parser.parse_args()

    # Create the Couchbase connection, and bail if it doesn't work
    cb = Couchbase.connect(host=args.couchbase_host,
                           bucket=args.couchbase_bucket,
                           password=args.couchbase_password)

    # Now just loop through and create documents. I like counters, so there's
    # one to tell me how much has been done. I also like timers, so there's one
    # of them too.
    counter = 0
    start_time = time.time()
    for doc in _all_docs_by_page(args.db, args.page_size):
        # Assume we don't want design documents, since they're likely to be
        # already stored elsewhere (e.g. in version control)
        if doc['id'].startswith("_design"):
            continue

        # Clean up the document a bit. Couchbase doesn't care about special
        # fields like '_id' and '_rev', so remove them
        if '_id' in doc['doc']:
            del doc['doc']['_id']

        if '_rev' in doc['doc']:
            del doc['doc']['_rev']

        # Couchbase has a maximum key length of 250 bytes, while CouchDB has no
        # such restrictions. If the key is > 250 bytes, we have a potential
        # problem. 
        # Hack around it for now by encoding the key to a hash if it's too long.
        key = _encode_key_if_necessary(doc['id'])
        cb.set(key, doc['doc'])

        counter += 1
        sys.stderr.write(str(counter) + '\r')
        sys.stderr.flush()

    # A little final message
    sys.stderr.write("Done! {0} documents in {1} seconds!\n".format(
        counter, time.time() - start_time))
