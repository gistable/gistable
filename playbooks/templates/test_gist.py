"""Test a Python snippet.

1. Download
2. Attempt to run
3. Catch/Log error
4. Parse, log, and pip install dependencies
5. Attempt to run
6. Catch/Log error
"""


# Imports
from __future__ import with_statement
from visitor import ParserVisitor
import ast
import httplib
import logging
import os
import signal
import subprocess
import sys


# Configure logging
logging.basicConfig(format='%(asctime)-15s %(message)s')
logger = logging.getLogger('test_gist')
logger.setLevel(logging.INFO)


# Seconds for timeout
TIMEOUT_SECONDS = 5


class timeout:
    """Timeout class.

    Taken from StackOverflow: https://stackoverflow.com/a/22348885
    """

    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        logger.info('Timeout encountered')
        raise TimeoutError(self.error_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        signal.alarm(0)


class TimeoutError(Exception):
    pass


def _log(key, value, client_addr):
    """Log data to a Consul key/value store.

    Parameters
    ----------
    key : string
        Key for which to log the value
    value : string
        Value being logged
    client_addr : string
        Consul client address
    """
    conn = httplib.HTTPConnection(client_addr)
    conn.request('PUT', '/v1/kv/{}'.format(key), body=str(value))
    conn.getresponse()
    conn.close()


def test_gist(gist, consul_addr='127.0.0.1:8500'):
    """Run gist tests"""

    # Get gist id
    gist_id = gist.split('/')[-1]
    logger.info('Processing Gist: ' + gist_id)

    # Log gist url
    _log(gist_id + '/url', gist, consul_addr)

    # Run tests
    try:

        # Attempt to git clone the gist into the directory `gist`
        logger.info('Cloning...')
        with timeout(seconds=TIMEOUT_SECONDS):
            subprocess.call(['git', 'clone', '--depth=1', gist, 'gist'])
            logger.info('Clone complete')

        # Find snippet file
        snippet_filename = os.path.join(
            'gist',
            filter(lambda f: os.path.basename(f) != '.git', os.listdir('gist'))[0]
        )

        # Read snippet
        logger.info('Reading snippet...')
        with open(snippet_filename, 'r') as snippet_file:
            snippet = snippet_file.read()

        # Store snippet code
        _log(gist_id + '/snippet.py', snippet, consul_addr)
        logger.info('Read complete')

        # Execute snippet
        logger.info('Initial-Eval...')
        try:
            try:
                with timeout(seconds=TIMEOUT_SECONDS):
                    execfile(snippet_filename, {}, {})
            except TimeoutError:
                pass
            import_error = False
            logger.info('No Error')
            _log(gist_id + '/initial-eval/result', 'Success', consul_addr)
        except BaseException as e:
            import_error = (type(e).__name__ == 'ImportError')
            logger.info('Error')
            _log(gist_id + '/initial-eval/result', type(e).__name__, consul_addr)
            _log(gist_id + '/initial-eval/message', str(e), consul_addr)

        # If caught an import error, parse and pip install packages
        if import_error:

            # Parse snippet
            logger.info('Parsing snippet...')
            visitor = ParserVisitor()
            visitor.visit(ast.parse(snippet))
            imports = visitor.import_libraries

            # Map to base name
            imports = [i.split('.')[0] for i in imports]

            # Log imports
            _log(gist_id + '/imports', '\n'.join(imports), consul_addr)

            # pip install imports
            logger.info('Installing imports...')
            try:
                for i in imports:
                    subprocess.call(['pip', 'install', i])
            except BaseException as e:
                logger.info('PIP Error')
                _log(gist_id + '/pip/error', type(e).__name__, consul_addr)
                _log(gist_id + '/pip/message', str(e), consul_addr)

            # Execute snippet again
            logger.info('Final-Eval...')
            try:
                try:
                    with timeout(seconds=TIMEOUT_SECONDS):
                        execfile(snippet_filename, {}, {})
                except TimeoutError:
                    pass
                logger.info('Success')
                _log(gist_id + '/final-eval/result', 'Success', consul_addr)
            except BaseException as e:
                logger.info('Error')
                _log(gist_id + '/final-eval/result', type(e).__name__, consul_addr)
                _log(gist_id + '/final-eval/message', str(e), consul_addr)

    except BaseException as e:

        # Log error
        logger.error('Unknown Error: ' + type(e).__name__)
        _log(gist_id + '/error/type', type(e).__name__, consul_addr)
        _log(gist_id + '/error/message', str(e), consul_addr)


def main():
    """Execute main."""

    # Get argv
    argv = sys.argv[1:]
    if len(argv) != 1 and len(argv) != 2:
        raise Exception('Usage: python test_gist.py <gist url> [consul addr]')

    # Test gist
    test_gist(*argv)


# Invoke main
if __name__ == '__main__':
    main()
