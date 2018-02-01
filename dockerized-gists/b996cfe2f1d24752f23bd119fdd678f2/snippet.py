#!/usr/bin/env python
# encoding: utf-8
"""A script for downloading (crawling) tweets by their IDs. 
A useful tool for creating datasets of tweets, as requested in popular research challenges on Twitter data 
(e.g., SemEval, #Microposts and TREC Microblog Track). 
It requires Twython (it optionally requires bz2file for compression).
This code is in https://gist.github.com/giacbrd/b996cfe2f1d24752f23bd119fdd678f2"""

__author__ = 'Giacomo Berardi <giacbrd.com>'

import io, json, time, os, logging, argparse, atexit, gzip, sys
from tempfile import NamedTemporaryFile
from twython import Twython
from twython.exceptions import TwythonError, TwythonRateLimitError

# Minimal time accepted between two Rate Limit Errors
TOO_SOON = 10
# Time to wait if we receive a Rate Limit Error too soon after a previous one
WAIT_SOME_MORE = 60

# Default values set according to https://dev.twitter.com/rest/reference/get/statuses/show/%3Aid
SLEEP_SECS_DEFAULT = 0
REQUEST_LIMIT_DEFAULT = 180
BATCH_TIME_DEFAULT = 15 * 60

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def check_negative(value):
    value = int(value)
    if value < 0:
        raise argparse.ArgumentTypeError('%s is an invalid positive int value' % value)
    return value


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-i', '--input', required=False, help='Tweets IDs file, first element of each line is an ID. '
                                                          'If not set, the standard input is read.')
parser.add_argument('-o', '--output', required=True,
                    help='Tweets dataset in jsonl: a complete Twython tweet json per line. One can set the same '
                         'output file for several runs of this script: already downloaded tweets '
                         'are not re-processed, new tweets are appended.')
parser.add_argument('-r', '--responses', required=False,
                    help='If set, it outputs a json map from the http response statuses to the tweet IDs.')
parser.add_argument('-s', '--sleep', required=False, default=SLEEP_SECS_DEFAULT, type=check_negative,
                    help='Time to wait between each request, in seconds.')
parser.add_argument('-l', '--limit', required=False, default=REQUEST_LIMIT_DEFAULT, type=check_negative,
                    help='Number of requests before stopping for wating the "totaltime" passed since the first request.')
parser.add_argument('-t', '--totaltime', required=False, default=BATCH_TIME_DEFAULT, type=check_negative,
                    help='Window time necessary for each batch of "limit" requests, in seconds.')
parser.add_argument('-c', '--compress', required=False, choices=['bz2', 'gzip'],
                    help='Chose the compression format for the out files, no extension is appended.')
parser.add_argument('--consumerkey', required=True, help='Consumer key.')
parser.add_argument('--consumersecret', required=True, help='Consumer secret.')
parser.add_argument('--accesstoken', required=True, help='Access token.')
parser.add_argument('--accesssecret', required=True, help='Access token secret.')
parser.add_argument('--test', required=False, action='store_true', default=False,
                    help='If set, run some tests for this script. All other parameters are ignored, '
                         'except for the authentication codes.')
args = parser.parse_args()

in_path = args.input
out_path = args.output
responses_path = args.responses
sleep_secs = args.sleep
request_limit = args.limit
batch_time = args.totaltime
compression = args.compress
do_test = args.test

start = -1
responses_store = {}

# http://stackoverflow.com/questions/13044562/python-mechanism-to-identify-compressed-file-type-and-uncompress
_SIGNATURES = {
    '\x1f\x8b\x08': 'gzip',
    '\x42\x5a\x68': 'bz2'
    # '\x50\x4b\x03\x04': 'zip'
}
_MAX_SIGN_LEN = max(len(x) for x in _SIGNATURES)


def which_compression(path):
    with open(path) as f:
        file_start = f.read(_MAX_SIGN_LEN)
    for signature, file_type in _SIGNATURES.items():
        if file_start.startswith(signature):
            return file_type


def get_open(path, mode, file_type=None, encoding='utf-8'):
    def wrapper(opener):
        if 'r' in mode:
            return io.TextIOWrapper(io.BufferedReader(opener), encoding=encoding)
        else:
            return io.TextIOWrapper(opener, encoding=encoding)

    if file_type == 'gzip':
        return wrapper(gzip.GzipFile(path, mode))
    if file_type == 'bz2':
        import bz2file
        return wrapper(bz2file.BZ2File(path, mode))
    else:
        return io.open(path, mode, encoding=encoding)


def dump_responses():
    global responses_path, responses_store, compression
    if responses_path and responses_store:
        with get_open(responses_path, 'w', compression) as responses_out:
            responses_out.write(unicode(json.dumps(responses_store)))


def log(msg, id=None):
    if id is not None:
        logger.info('%s: %s' % (id, msg))
    else:
        logger.info('%s' % msg)


def wait():
    global start
    # Wait a total of batch_time
    time.sleep((batch_time - (time.time() - start)) + 1)
    start = time.time()


def save_response(responses_dict, id, status_code):
    if status_code not in responses_dict:
        responses_dict[status_code] = []
    responses_dict[status_code].append(id)


def download(in_path, out_path, twitter, responses_store=None, sleep_secs=SLEEP_SECS_DEFAULT,
             batch_time=BATCH_TIME_DEFAULT, request_limit=REQUEST_LIMIT_DEFAULT, compression=False):
    global start
    start = time.time()
    seen = frozenset()
    if os.path.exists(out_path):
        with get_open(out_path, 'r', which_compression(out_path)) as current:
            seen = frozenset(json.loads(line.strip())['id'] for line in current)
    count = 0
    with (get_open(in_path, 'r', which_compression(in_path)) if in_path else sys.stdin) as input_stream:
        with get_open(out_path, 'a', compression) as out:
            for line in input_stream:
                id = int(line.strip().split()[0])
                if id in seen:
                    log('Already downloaded', id)
                    continue
                try:
                    while True:
                        try:
                            tweet = twitter.show_status(id=id)
                            out.write(unicode(json.dumps(tweet) + '\n'))
                        except TwythonRateLimitError as e:
                            # If this error is received after only few calls (10 seconds of calls) wait just a minute
                            if time.time() - start < TOO_SOON and count > 0:
                                log('Waiting %s seconds more for resuming download after recurrent rate limit error ...'
                                    % WAIT_SOME_MORE)
                                time.sleep(WAIT_SOME_MORE)
                            else:
                                log(e, id)
                                log('Waiting %s seconds for resuming download after rate limit error ...'
                                    % (batch_time - (time.time() - start)))
                                wait()
                            continue
                        count += 1
                        break
                except TwythonError as e:
                    log(e, id)
                    if responses_store is not None and isinstance(responses_store, dict):
                        save_response(responses_store, id, e.error_code)
                    continue
                finally:
                    if sleep_secs:
                        time.sleep(sleep_secs)
                    if count > 0 and count % request_limit == 0:
                        log('Waiting %s seconds for resuming download after rate limit check of %s calls ...'
                            % (batch_time - (time.time() - start), request_limit))
                        wait()
                if responses_store is not None and isinstance(responses_store, dict):
                    save_response(responses_store, id, 200)
                log('Done!', id)


def test():
    log('Testing...')
    with NamedTemporaryFile() as temp_input:
        with NamedTemporaryFile() as temp_output:
            temp_input.write('20\n10')
            temp_input.seek(0)
            temp_resp = {}
            download(temp_input.name, temp_output.name,
                     Twython(args.consumerkey, args.consumersecret, args.accesstoken, args.accesssecret),
                     temp_resp, 0, BATCH_TIME_DEFAULT, REQUEST_LIMIT_DEFAULT, 'bz2')
            assert temp_resp == {200: [20], 404: [10]}
            assert 'twttr' in json.loads(get_open(temp_output.name, 'r', 'bz2').read().strip())['text']
            log('Test passed!')


if __name__ == '__main__':
    if do_test:
        test()
    else:
        twitter = Twython(args.consumerkey, args.consumersecret, args.accesstoken, args.accesssecret)
        atexit.register(dump_responses)
        download(in_path, out_path, twitter, responses_store if responses_path else None, sleep_secs, batch_time,
                 request_limit, compression)
