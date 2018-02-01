#!/usr/bin/env python
# Copyright © 2016 Dan Sheridan <dan.sheridan@postman.org.uk>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See http://www.wtfpl.net/ for more details.

import salt.client
import argparse
import sys
import fnmatch
import unittest

# Filter out results from state modules that don't have useful test
# such as svn.latest and pkg.refresh_db.
# Represent as a list of 4-tuples of globs: (module, state_id, state_name, function)
ignore = [ ('pkg', None, None, 'refresh_db'),
           ('svn', None, None, 'latest'),
           ('module', None, 'chocolatey.bootstrap', 'run'),
           ('rdp', None, None, 'enabled'),
           ('file', None, '[cC]:*', 'managed'),  # Windows minions lie about files with test=true
           ('file', None, '[cC]:*', 'recurse'),
           ('network', None, None, 'managed'), # Windows minions erroneously report that the interface will be enabled
]


# function to match patterns against state results
def matchstate(stateresult, pattern):
    for s, p in zip(stateresult.split('|'), pattern):
        if p and not fnmatch.fnmatch(s.rstrip('_').lstrip('-'), p): return True
    return False

# main

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Check if a minion's state is up-to-date.")
    parser.add_argument('hostname', help='The name of the minion to be checked')

    args = parser.parse_args()

    hostname = args.hostname

    client = salt.client.LocalClient()
    result = client.cmd(hostname, 'state.highstate', timeout=300, arg=['test=True'])

    if len(result) == 0:
        sys.stdout.write("UNKNOWN: timed out waiting for state.highstate\n")
        sys.exit(3)

    # find all the states that don't have a True result -- pending changes or problems
    bad_states = [(state, data['result']) for state,data in result.get(hostname, {}).items() if not data['result']]

    # filter out the ones that we are ignoring
    for pattern in ignore:
        bad_states = filter(lambda x: matchstate(x[0], pattern), bad_states)

    changes_states = filter(lambda x: x[1] == None, bad_states)
    broken_states = filter(lambda x: x[1] == False, bad_states)

    bad_states_text = ''
    for state in bad_states:
        description = state[0].split('|')[:2]
        description = map(lambda d: d.strip('-_'), description) # tidy up the text
        bad_states_text += ':'.join(description) + '\n'

    if broken_states:
        sys.stdout.write("CRITICAL: %s broken states, %s pending changes\n%s" % (len(broken_states), len(changes_states), bad_states_text))
        sys.exit(2)
    if changes_states:
        sys.stdout.write("WARNING: %s pending changes\n%s" % (len(changes_states), bad_states_text))
        sys.exit(1)
    else:
        sys.stdout.write("OK: minion is up to date\n")
        sys.exit(0)

## Testing
# run tests with: python -m unittest check_salt_state

class Test(unittest.TestCase):
    longMessage = True

    def test_match(self):
	self.assertFalse(matchstate('svn_|blah|blah|-latest', ('svn', None, None, 'latest')))

    def test_partial_match(self):
	self.assertTrue(matchstate('svn_|blah|blah|-update', ('svn', None, None, 'latest')))

    def test_not_a_match(self):
	self.assertTrue(matchstate('file_|blah|blah|-update', ('svn', None, None, 'latest')))

    def test_with_a_glob(self):
	self.assertFalse(matchstate('file_|blah|blah|-update', ('file', None, None, 'up*')))
