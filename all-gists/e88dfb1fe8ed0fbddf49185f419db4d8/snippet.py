# -*- coding: utf-8 -*-
#
# Author: Daniel Garcia (cr0hn) - @ggdaniel
# Github: https://github.com/cr0hn
#


import asyncio

from multiprocessing import Process
from threading import Thread, Event, BoundedSemaphore, currentThread


class _ConcurrentManager(object):

	def __init__(self, n_process=2, n_threads=5, n_tasks=10, daemon=False):
		"""
		:param n_process:
		:type n_process:

		:param n_threads:
		:type n_threads:

		:param n_tasks:
		:type n_tasks:

		:param daemon:
		:type daemon:
		"""
		self.daemon = daemon
		self.n_taks = n_tasks
		self.n_threads = n_threads
		self.n_process = n_process

		self.sem_threads = BoundedSemaphore(self.n_threads)
		self.sem_tasks = asyncio.BoundedSemaphore(self.n_taks)

		self.running_process = []

	# --------------------------------------------------------------------------
	# Public methods
	# --------------------------------------------------------------------------
	def run(self):
		self._launch_processes()

	def wait_until_complete(self):
		try:
			for x in self.running_process:
				x.join()
		except KeyboardInterrupt:
			print("\n[*] CTRL+C Caught. ...")

			for x in self.running_process:
				x.terminate()

	# --------------------------------------------------------------------------
	# Private launchers
	# --------------------------------------------------------------------------

	# Asyncio task launcher
	def _launch_tasks(self, name, state, sem):

		loop = asyncio.new_event_loop()
		asyncio.set_event_loop(loop)

		try:
			loop.run_until_complete(self._tasks_worker_manager(loop, name, state))
		except KeyboardInterrupt:

			# Canceling tasks
			tasks = asyncio.Task.all_tasks()

			map(asyncio.Task.cancel, tasks)

			loop.run_forever()
			tasks.exception()
		finally:
			loop.close()
			sem.release()

	# Thread launcher the pool
	def _launch_threads(self, proc_number):
		state = Event()

		th = []

		try:
			while True:

				if state.isSet():
					break

				n = "proc-%s" % proc_number
				t = Thread(target=self._launch_tasks, args=(n, state, self.sem_threads,))

				th.append(t)

				# t.daemon = True
				t.start()

				self.sem_threads.acquire()

			for t in th:
				t.join()

		except KeyboardInterrupt:
			# print("\n[*] CTRL+C Caught. Exiting threads form process '%s'..." % proc_number)
			pass
		finally:

			state.set()

	# Process launcher the pool
	def _launch_processes(self):

		try:
			for i in range(self.n_process):
				p = Process(target=self._launch_threads, args=(i,))

				if self.daemon is True:
					p.daemon = True

				self.running_process.append(p)

				p.start()

			if self.daemon is False:
				for x in self.running_process:
					x.join()

		except KeyboardInterrupt:

			for x in self.running_process:
				x.terminate()

	# --------------------------------------------------------------------------
	# Scalability methods
	# --------------------------------------------------------------------------
	@property
	def threads_num(self):
		"""
		:return: Return the current active threads
		:rtype: int
		"""
		return self.sem_threads._value

	def threads_inc(self, n):
		"""
		Increases the thread pool in 'n'.

		:param n: number which increment the thread pool
		:type n: int
		"""
		self.sem_threads._value += n

		if self.sem_threads._value < self.sem_threads._initial_value:
			self.sem_threads.release()

	def threads_dec(self, n):
		"""
		Decreases the threads number in 'n'

		:param n: number which decrement the thread pool
		:type n: int
		"""
		if n > 0:
			if self.sem_threads._value - n > 1:
				self.sem_threads._value -= n

	@property
	def tasks_num(self):
		"""
		:return: Return the current active asyncio tasks
		:rtype: int
		"""
		return self.sem_tasks._value

	def tasks_inc(self, n):
		"""
		Increases the asyncio tasks pool in 'n'.

		:param n: number which increment the asyncio Task pool
		:type n: int
		"""
		self.sem_tasks._value += n

		if self.sem_tasks._value < self.sem_tasks._bound_value:
			self.sem_tasks.release()

	def tasks_dec(self, n):
		"""
		Decreases the asyncio Tasks number in 'n'

		:param n: number which decrement the tasks pool
		:type n: int
		"""
		if n > 0:
			if self.sem_tasks._value - n > 1:
				self.sem_tasks._value -= n


class SimpleConcurrencyManager(_ConcurrentManager):
	
	def __init__(self, co_to_run, n_process=2, n_threads=5, n_tasks=10, daemon=False):
		self.co_to_run = co_to_run

		super(SimpleConcurrencyManager, self).__init__(n_process, n_threads, n_tasks, daemon)

	# Task pool
	@asyncio.coroutine
	def _tasks_worker_manager(self, loop, name, state):

		while True:
			if state.isSet():
				break

			yield from self.sem_tasks.acquire()

			loop.create_task(self.co_to_run(name, state))


class AdvancedConcurrencyManager(_ConcurrentManager):

	def __init__(self, coro_map, n_process=2, n_threads=5, n_tasks=10, daemon=False):
		"""
		coro_map is a dict with pointer to coroutines and the number os task assigned to each one.

		Example:
		>>> fn_map = (
			(coro_fn_1, 3),
			(coro_fn_2, 4),
			(coro_fn_3, 3),
		)
		>>> c = AdvancedConcurrencyManager(coro_map=fn_map)
		>>> c.run()

		"""
		self.co_to_run = coro_map
		self.round_robin_round = []
		self.turn = 0

		# Build a Semaphore per each coro function
		for coro_fn, instances in coro_map:

			for x in range(instances):
				# Add priority fn
				self.round_robin_round.append(coro_fn)

		if len(self.round_robin_round) != n_tasks:
			raise ValueError("The summation of all of tasks slots do not match with the tasks number")

		super(AdvancedConcurrencyManager, self).__init__(n_process, n_threads, n_tasks, daemon)

	# Task pool
	@asyncio.coroutine
	def _tasks_worker_manager(self, loop, name, state):

		while True:
			if state.isSet():
				break

			# Get the round turn
			coro_next = self.round_robin_round[self.turn]

			# Set next turn
			self.turn += 1
			if self.turn >= len(self.round_robin_round):
				self.turn = 0

			yield from self.sem_tasks.acquire()

			loop.create_task(coro_next(name, state))


@asyncio.coroutine
def task1(t, e):
	"""
	A task

	:param e: Event obj
	:type e: Event
	"""
	import random

	for x in range(200):
		print(t, " - ", currentThread().name, " - task-1-%s" % random.randint(1, 100000))
		yield from asyncio.sleep(1)


@asyncio.coroutine
def task2(t, e):
	"""
	A task

	:param e: Event obj
	:type e: Event
	"""
	import random

	for x in range(200):
		print(t, " - ", currentThread().name, " - task-2-%s" % random.randint(1, 100000))
		yield from asyncio.sleep(1)


if __name__ == '__main__':

	#
	# This code build this process-> threads-> asyncio tasks distribution:
	#
	#   main -> Process 1 -> Thread 1.1 -> Task 1.1.1
	#                                   -> Task 1.1.2
	#                                   -> Task 1.1.3
	#
	#                     -> Thread 1.2
	#                                   -> Task 1.2.1
	#                                   -> Task 1.2.2
	#                                   -> Task 1.2.3
	#
	#           Process 2 -> Thread 2.1 -> Task 2.1.1
	#                                   -> Task 2.1.2
	#                                   -> Task 2.1.3
	#
	#                     -> Thread 2.2
	#                                   -> Task 2.2.1
	#                                   -> Task 2.2.2
	#                                   -> Task 2.2.3
	import time

	# c = ConcurrentManager(n_process=1, n_taks=2, n_threads=2, daemon=True)
	# c = SimpleConcurrencyManager(task1, n_process=1, n_threads=10, n_tasks=20)
	# c.run()

	tasks = (
		(task1, 2),
		(task2, 8)
	)
	c = AdvancedConcurrencyManager(tasks, n_process=2, n_threads=10, n_tasks=10)
	c.run()
