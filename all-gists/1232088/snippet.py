import fcntl
import os
from subprocess import *

def non_block_read(output):
    fd = output.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    try:
        return output.read()
    except:
        return ""

############
# Use case #
############

sb = Popen("echo test; sleep 10000", shell=True, stdout=PIPE)
sb.kill()
sb.poll() # return -9
#sb.stdout.read() # Will block and will block forever cause nothing will come out since the job is done
non_block_read(sb.stdout) # will return '' instead of hanging for ever

