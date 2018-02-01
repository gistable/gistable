from subprocess import Popen, PIPE
from os import path

git_command = ['/usr/bin/git', 'status']
repository  = path.dirname('/path/to/dir/') 

git_query = Popen(git_command, cwd=repository, stdout=PIPE, stderr=PIPE)
(git_status, error) = git_query.communicate()
if git_query.poll() == 0:
   # Do stuff