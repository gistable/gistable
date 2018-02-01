"""Scrape gists from a consul API."""
from __future__ import with_statement
import sys
import urllib
import json
import base64
import csv
import logging
import os


# Configure logging
logging.basicConfig(format='%(asctime)-15s %(message)s')
logger = logging.getLogger('scrape_gist')
logger.setLevel(logging.INFO)


def main():

    # Get arguments
    argv = sys.argv[1:]
    if len(argv) != 1:
        raise Exception('Usage: python scrape_consul_gists.py <consul addr>')
    base_addr = argv[0]

    # Get all gist ids known by consul
    response = urllib.urlopen('{}/v1/kv/?recurse=true&keys'.format(base_addr))
    gist_ids = set((k.split('/')[0] for k in json.loads(response.read())))

    # Init results list
    results = []

    # For each gist, load data
    for idx, gist_id in enumerate(gist_ids):

        # Debug
        logger.info('{}/{} --- {}'.format(idx + 1, len(gist_ids), gist_id))

        # Get all associated keys
        response = urllib.urlopen('{}/v1/kv/{}?recurse=true'.format(base_addr, gist_id))
        keys = {
            '/'.join(k.get('Key', '').split('/')[1:]): base64.b64decode(k.get('Value', '') or '')
            for k in json.loads(response.read())
        }

        # Keys
        initial_eval_key = 'initial-eval/result'
        final_eval_key = 'final-eval/result'

        # Result dict
        results.append({
            'id': gist_id,
            'url': keys.get('url', ''),
            'initial-eval': keys.get(initial_eval_key, ''),
            'final-eval': keys.get(final_eval_key, ''),
            'error': keys.get('error/result', '')
        })

        # If a snippet never got recorded, skip download steps
        if 'snippet.py' not in keys:
            continue

        # Log for scripts that succeeded the first time
        if (initial_eval_key in keys
                and keys.get(initial_eval_key, '') == 'Success'):

            # Make directory
            dir = 'gists/{}/'.format(gist_id)
            if not os.path.exists(dir):
                os.makedirs(dir)

            # Write snippet file and dockerfile
            snippet_filename = dir + 'snippet.py'
            dockerfile_fielname = dir + 'Dockerfile'
            with open(snippet_filename, 'w') as snippet, open(dockerfile_fielname, 'w') as dockerfile:

                # Write snippet
                snippet.write(keys.get('snippet.py', ''))

                # Write dockerfile
                lines = [
                    'FROM python:2.7.13',
                    'ADD snippet.py snippet.py',
                    'CMD ["python", "snippet.py"]'
                ]
                dockerfile.write('\n'.join(lines))

        # Look for scripts that failed due to import the first time,
        # but failed for a different reason the after installing dependencies
        elif (initial_eval_key in keys
                and final_eval_key in keys
                and keys.get(initial_eval_key, '') == 'ImportError'
                and keys.get(final_eval_key, '') != 'ImportError'):

            # Make directory
            dir = 'gists/{}/'.format(gist_id)
            if not os.path.exists(dir):
                os.makedirs(dir)

            # Write snippet file and dockerfile
            snippet_filename = dir + 'snippet.py'
            dockerfile_fielname = dir + 'Dockerfile'
            with open(snippet_filename, 'w') as snippet, open(dockerfile_fielname, 'w') as dockerfile:

                # Write snippet
                snippet.write(keys.get('snippet.py', ''))

                # Write dockerfile
                lines = [
                    'FROM python:2.7.13',
                    'ADD snippet.py snippet.py',
                ]
                lines += [
                    'RUN ["pip", "install", "{}"]'.format(d)
                    for d in keys.get('imports', '').split()
                ]
                lines += ['CMD ["python", "snippet.py"]']
                dockerfile.write('\n'.join(lines))

        # Download all the other snippets to a separate directory
        else:

            # Make directory
            dir = 'gists-other/{}/'.format(gist_id)
            if not os.path.exists(dir):
                os.makedirs(dir)
            snippet_filename = dir + 'snippet.py'

            # Write snippet
            with open(snippet_filename, 'w') as snippet:
                snippet.write(keys.get('snippet.py', ''))

    # Write output file
    with open('gists.csv', 'w') as results_file:

        # Row fieldnames
        fieldnames = ['id', 'url', 'initial-eval', 'final-eval', 'error']

        # Create dict writer
        writer = csv.DictWriter(results_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == '__main__':
    main()
