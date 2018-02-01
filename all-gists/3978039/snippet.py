import re
import logbook
from pprint import pprint
import time
import sys

import threading
import Queue
import multiprocessing

import credential_utils
from imap_utils import GIMAPFetcher

class Timer(object):
	'''Timer for a _with_ block'''
	def __init__(self, msg = None):
		self.msg = msg
	def __enter__(self):
		self.start = time.time()
	def __exit__(self, *args):
		elapsed = time.time() - self.start
		if self.msg:
			print "%s: %f" % (self.msg, elapsed)		
		else:
			print elapsed

def connect(login):
	'''Connect to IMAP server with gmvault credential'''
	logbook.NullHandler().push_application()
	credential = credential_utils.CredentialHelper.get_credential(
		{'email': login, 'passwd': 'not_seen', 'oauth': 'empty'})

	imap = GIMAPFetcher('imap.gmail.com', 993, login, credential,
		readonly_folder = True)
	imap.connect(go_to_all_folder = True)
	return imap

def search(imap, count):
	'''Find the first _count_ messages in the current mailbox'''
	req = '1:%d' % (count,)
	return imap.search({'type': 'imap', 'req': req})

def subject(msg):
	'''Find the subject of an email message, as returned from fetch()'''
	md = re.search(r'^Subject: ([^\n\r]*)', msg[GIMAPFetcher.EMAIL_BODY],
		re.M | re.I)
	return md.group(1) if md else None

def fetch_subject(imap, i):
	'''Fetch message number _i_, and get its subject'''
	msg = imap.fetch(i, GIMAPFetcher.GET_ALL_INFO)[i]
	return subject(msg)

def subjects_single(imap, ids):
	return sum(len(fetch_subject(imap, i)) for i in ids)


def subjects_thread(login, ids, poolsize):
	inq = Queue.Queue()		# ids to process
	outq = Queue.Queue()	# resulting subject lines
	def worker():
		imap = connect(login)
		while True:
			i = inq.get()
			if not i: # 'None' marks no more data
				break
			outq.put(fetch_subject(imap, i))
	
	for i in ids:
		inq.put(i)
	
	ts = []
	for n in range(poolsize):
		t = threading.Thread(target = worker)
		ts.append(t)
		t.start()
		inq.put(None) # tell each thread we're done
	
	for t in ts:	# wait for threads to finish
		t.join()
	
	r = []
	try:
		while True:
			s = outq.get(block = False)
			r.append(s)
	except Queue.Empty:
		pass
	return sum(len(x) for x in r)


process_imap = None	# gotta use globals for initializing mp.Pool

def mp_process(i):
	global process_imap
	return fetch_subject(process_imap, i)
	
def subjects_process(login, ids, poolsize):
	def init():
		global process_imap
		process_imap = connect(login)
	pool = multiprocessing.Pool(poolsize, init)
	s = pool.map(mp_process, ids)
	return sum(len(x) for x in s)


if __name__ == '__main__':
	if len(sys.argv) != 3:
		print "Test the speed of parallel fetching from Gmail"
		print "Usage: speed.py GMAIL_ACCOUNT NUMBER_OF_MESSAGES"
		sys.exit(1)
		
	login = sys.argv[1]
	count = int(sys.argv[2])

	imap = connect(login)
	ids = search(imap, count)

	with Timer('single threaded'):
		print subjects_single(imap, ids)

	with Timer('multi threaded'):
		print subjects_thread(login, ids, 5)

	with Timer('processes'):
		print subjects_process(login, ids, 5)
