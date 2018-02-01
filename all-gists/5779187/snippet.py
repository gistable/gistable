import sys
from subprocess import PIPE, Popen
from threading  import Thread

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

ON_POSIX = 'posix' in sys.builtin_module_names

def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()

def execute(cmd,path):
  p = Popen(cmd, stdout=PIPE, bufsize=1, close_fds=ON_POSIX, shell=True, cwd=path)
	q = Queue()
	t = Thread(target=enqueue_output, args=(p.stdout, q))
	t.daemon = True # thread dies with the program
	t.start()
	# read line without blocking
	try:  line = q.get_nowait() # or q.get(timeout=.1)
	except Empty:
	    print('no output yet')
	else:
		print line