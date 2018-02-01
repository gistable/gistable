#!/usr/local/bin/python
"""
To use this script, you must be in the root directory of a Rails project that
is using git. You should also make sure that your directory does not contain any
uncommitted changes. Then run:

    $ python rails_switch_branch.py name_of_another_branch

Running the above will do the following:

    1. Roll back any migrations on your current branch which do not exist on the
    other branch
    2. Discard any changes to the db/schema.rb file
    3. Check out the other branch
    4. Run any new migrations existing in the other branch
    5. Update your test database

TODO:
    - Check if git directory is dirty. If so, do not run.
"""
import sys
import subprocess
import re

BRANCH_NAME = sys.argv[1]

print "*** Switching from current branch to: " + BRANCH_NAME

files_changed = subprocess.check_output(("git diff " + BRANCH_NAME + " --name-status").split())
migrations = re.findall("A\\tdb/migrate/([0-9]+)", files_changed)

for migration in reversed(migrations):
  sh_command = "bundle exec rake db:migrate:down VERSION=" + migration
  print "*** Running: " + sh_command
  print
  subprocess.call(sh_command.split())

print "*** Discarding any changes to db/schema.rb"
print
subprocess.call("git checkout db/schema.rb".split())
subprocess.call(("git checkout " + BRANCH_NAME).split())

print
print "*** Running: bundle exec rake db:migrate"
print
subprocess.call("bundle exec rake db:migrate".split())

print "*** Running: bundle exec rake db:test:prepare"
print
subprocess.call("bundle exec rake db:test:prepare".split())

print
print '*** Successfully switched branches and migrated to "' + BRANCH_NAME + '"'
print