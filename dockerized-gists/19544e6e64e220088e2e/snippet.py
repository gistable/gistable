from contextlib import contextmanager
from sys import stderr
from timeit import default_timer as now
import atexit

@contextmanager
def timeit(s=''):
	start = now()
	yield
	print >>stderr, '-- %06.3fs' % (now() - start), '|', s

def new(s):
	if s in logs:
		print >>stderr, '-- waring "%s" already exists!' % s
	logs[s] = now()

def log(s=''):
	if s not in logs:
		print >>stderr, '-- waring "%s" does not exist!' % s
		print >>stderr, '-- %06.3fs' % (now() - logs['']), '|', s
	else:
		print >>stderr, '-- %06.3fs' % (now() - logs[s]), '|', s

@atexit.register
def atend():
	r = logs.pop('')
	for msg, start in logs.items():
		print >>stderr, '-- %06.3fs' % (now() - start), '|', msg
	print >>stderr, '-- %06.3fs' % (now() - r), '| Total runtime.'

logs = {'': now()}
