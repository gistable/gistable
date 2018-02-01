#!/usr/bin/env python

from subprocess import Popen
from subprocess import PIPE
import sys
import beatbox

# credentials to login to salesforce.com with
username = "user@example.org"
password = "Password[And Security Token If Needed]"

def main():
	refname = sys.argv[1]
	oldrev  = sys.argv[2]
	newrev  = sys.argv[3]

	# grab the list of commits in this update
	missed_revs = Popen(["git",  "rev-list", oldrev + ".." + newrev], stdout=PIPE).communicate()[0].split("\n")

	# grab the commit messages
	commit_msgs = []
	for rev in missed_revs:
		if (len(rev) > 0):
			msg = Popen(["git", "cat-file", "commit", rev], stdout=PIPE).communicate()[0]
			commit_msgs.append(msg)

	# login to salesforce.com
	sf = beatbox._tPartnerNS
	svc = beatbox.Client()
	loginResult = svc.login(username, password)
	
	# make chatter FeedPost objects, one for each commit message
	# feel free to parse and otherwize futz with msg as needed
	# if you want to commit messages to goto a group instead of
	# the users wall, swap the parentId value for the Id of the group
	posts = []
	for msg  in commit_msgs:
		post = { 'type' : 'FeedPost',
				 'body' : 'Git commit\r\n' + msg,
				 'ParentId' : str(loginResult[sf.userId]) }
		posts.append(post)
	
	svc.create(posts)
	
	return 0

if __name__ == "__main__":
	sys.exit(main())
