import os
import fcntl
import subprocess

def non_block_read(output):
    fd = output.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    try:
        return output.read()
    except EOFError:
        raise EOFError
    except Exception, e:
        pass

def run_cmd(cmd):
	try:
        p = subprocess.Popen(
            cmd, bufsize=10240, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, close_fds=True)
        while True:
            data = non_block_read(p.stdout)
            print data
            if p.poll() is not None:
           	    break
    except Exception, e:
        print e