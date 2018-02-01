"""
Opens the latest pull request registered to a JIRA ticket.
You can call it from the Liferay repo to check your current branch,
or you can pass in a ticket number as an argument.
"""

import json
import sys
import urllib2
import webbrowser

if len(sys.argv) > 1:
    TICKET = sys.argv[1]
else:
    import re
    import subprocess

    try:
        BRANCH_ALL = subprocess.Popen(('git', 'branch'), stdout=subprocess.PIPE)
        BRANCH = subprocess.check_output(('grep', r'^\* '), stdin=BRANCH_ALL.stdout)
        TICKET = re.sub(r'.*([A-Z]{3,}-\d+).*', r'\1', BRANCH)
    except subprocess.CalledProcessError:
        print """
Could not parse git branch.
Either call this script with a ticket number or from a git repo.
        """
        sys.exit()

TICKET_URL = "https://issues.liferay.com/rest/api/latest/issue/" + TICKET

try:
    RESPONSE_TEXT = urllib2.urlopen(TICKET_URL).read()
    RESPONSE_DICT = json.loads(RESPONSE_TEXT)
    PULL_REQUEST_URL = RESPONSE_DICT["fields"]["customfield_10421"]

    webbrowser.open(PULL_REQUEST_URL)
except AttributeError:
    print "No pull request found for JIRA ticket number '" + TICKET + "'"
    sys.exit()
except urllib2.HTTPError:
    print "No JIRA ticket found for ticket number '" + TICKET +"'"
    sys.exit()
except urllib2.URLError:
    print "No internet connection available."
    sys.exit()
finally:
    sys.exit()
