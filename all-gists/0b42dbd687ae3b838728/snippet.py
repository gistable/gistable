#! /usr/bin/env python

import git
from time import localtime, strftime
from subprocess import call

crime = git.Repo("/Users/chadblack/Projects/crime")

call(["jrnl",strftime("%H:%M", localtime(crime.head.commit.committed_date))+":",crime.head.commit.message,"@"+crime.description])

