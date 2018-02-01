#!/usr/bin/env python

import sys
import kerberos
import optparse

try:
    from nitrate import *
except ImportError:
    print "Please install python-nitrate and try again: https://github.com/psss/python-nitrate"
    sys.exit(-1)


def _fetch_data(arguments):

    for plan in arguments.plan:
        
        plan = TestPlan(arguments.plan)

        try:
            print "Test Plan: %s" % plan
            _print_plain(plan.testcases)
        except kerberos.GSSError, e:
            print "Please start a new kerberos session running the 'kinit' command and try again."
            sys.exit(-1)
        except Exception, e:
            print str(e)
            return


def _print_plain(testcases):
        # Loop through all test cases
        print "ID\tSummary\tCLI\tUI\tUnk"
        tests = [test for test in testcases if test.status.name == 'CONFIRMED']
        for test in tests:
            cli = ui = unknown = False
            # Figure out if this is a CLI or UI test
            if 'web' in str(test.components).lower():
                ui = test.automated
            elif 'cli' in str(test.components).lower():
                cli = test.automated
            else:
                unknown = test.automated

            print "[%s] - %s\t%s\t%s\t%s" % (test.id, test.summary, cli, ui, unknown)


if __name__ == "__main__":
    
    description = "Generates reports against TCMS Test Plans"
    usage = "Usage: %prog --plan <plan>"
    epilog = "Constructive comments and feedback can be sent to Og Maciel <omaciel at ogmaciel dot com>."
    version = "%prog version 0.1"
    
    p = optparse.OptionParser(usage=usage, description=description, epilog=epilog, version=version)
    p.add_option('--plan', type=str, dest='plan', help='The test plan ID. e.g. 7771')

    options, arguments = p.parse_args()
    
    # Make sure we're passing a test plan
    if not options.plan:
        p.print_help()
        sys.exit(-1)
    
    _fetch_data(options)