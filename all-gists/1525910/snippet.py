GOODS = []
URL = ["http://www.xxxxxxxxx.com/img/testimonials/1122052/13",".jpg"]
START = 21455795
THREADS = 50
DIE = False


class MyQueue(Queue):
	def __init__(self,*argv):
		self.num = START
		return Queue.__init__(self,*argv)
	def advance(self):
		self.num += 1
		self.put(self.num)
		

def next_num(start):
	while 1:
		yield start
		start += 1

def try_num(q):
	print "Thread starting..."
	while not DIE:
		q.advance()
		num = q.get()
		curr_url = str(num).join(URL)
		try:
			urllib2.urlopen(curr_url,timeout=2)
			GOODS.append(curr_url)
			print curr_url
		except urllib2.HTTPError:
			pass
		except urllib2.URLError as e:
			print e
	print "Thread dying..."

def check_threads(threads):
	alive = True
	for thread in threads.values():
		alive = thread.is_alive() and alive
	return alive

if __name__ == "__main__":
	q = MyQueue()
	threads = {}
	for i in range(0,THREADS):
		threads[i] = threading.Thread(target=try_num,args=(q,))
		threads[i].start()

	threads_running = check_threads(threads)
	while threads_running:
		try:
			time.sleep(1)
			threads_running  = check_threads(threads)
		except KeyboardInterrupt:
			DIE = True
