import gevent
from gevent.queue import JoinableQueue
from gevent import Greenlet
from gevent.pool import Group
from gevent import monkey
monkey.patch_socket()
monkey.patch_ssl()

import requests
from requests import Session

""" url for testing """
apartment1_urls = ['http://tw.yahoo.com/', 
        'http://www.google.com/', 
	'http://facebook.com/']

apartment2_urls = ['http://www.youtube.com/', 
        'http://www.stackoverflow.com/', 
	'http://pastebin.com/']


class ApartmentManager(Greenlet):
	def __init__(self, name, urls):
		Greenlet.__init__(self)
		self.JobQueue = JoinableQueue()
		self.name = name
		self.assigning = True
		self.urls = urls

	def assignJob(self,job):
		print 'Manager {0} -> {1}'.format(self.name, job)
		self.JobQueue.put(job)
		gevent.sleep(0)
	
	def _run(self):
		for url in self.urls:
			self.assignJob(url)
		self.assigning = False
	

class Worker(Greenlet):
	def __init__(self, name, manager):
		Greenlet.__init__(self)
		self.name = name
		self.manager = manager
		self.JobQueue = self.manager.JobQueue
		self.session = Session()
	
	def _do_work(self, url):
		response = self.session.get(url)
		self.response = response.status_code
	
	def _run(self):
		while True:
			""" imply there is no more job later """
			if self.JobQueue.empty() and not self.manager.assigning:
				print 'worker {0} of {1} done working'.format(self.name, self.manager.name)
				break

			""" imply currently no job, but may have some job later """
			if self.JobQueue.empty() and self.manager.assigning:
				gevent.sleep(0)
				continue

			if not self.JobQueue.empty():	
				url = self.JobQueue.get()
				print 'worker {0} of {1} <- {2}'.format(self.name, self.manager.name, url)
				try:
					self._do_work(url)
					print 'worker {0} of {1}-> {2} for {3}'.format(self.name, self.manager.name, self.response, url)
				finally:
					self.JobQueue.task_done()



class Apartment(object):
	def __init__(self, name):
		print 'Apartment {0} Ready to work'.format(name)
		self.name = name
		""" managers and workers are all member of the apartment"""
		self.members = Group()
		
		""" create two managers and add them to members"""
		self.managers = [ApartmentManager('John', apartment1_urls), 
				 ApartmentManager('Micky', apartment2_urls)]

		for manager in self.managers:
			manager.start()
			self.members.add(manager)

		self.workers = list()
		""" assign 5 worker for Manager John"""
		for i in range(2):
			self.workers.append(Worker(i, self.managers[0]))

		""" assign 5 worker for Manager Micky"""
		for i in range(2):
			self.workers.append(Worker(i, self.managers[1]))

		for worker in self.workers:
			worker.start()
			self.members.add(worker)
	
	def start(self):
		self.members.join()
		

testApartment = Apartment('test')
testApartment.start()
