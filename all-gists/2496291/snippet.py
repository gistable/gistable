#!/usr/bin/env python
#-*- coding:utf-8 -*-

from Queue import Queue


# ---------------------
# Corotine Task Manager
# ---------------------

class TaskManager(object):
    """A conrotine task manager."""

    def __init__(self, max_tasks_number=None):
        self.tasks = Queue(max_tasks_number)

    def add_task(self, task):
        self.tasks.put(task)

    def run(self):
        finished_tasks = []
        while not self.tasks.empty():
            current_task = self.tasks.get()
            try:
                next(current_task)
            except StopIteration:
                finished_tasks.append(current_task)
            else:
                self.tasks.put(current_task)
        return finished_tasks


# ----
# Demo
# ----

def print_a_to_z():
    for i in range(ord("a"), ord("z") + 1):
        print chr(i)
        yield


def print_A_to_Z():
    for i in range(ord("A"), ord("Z") + 1):
        print chr(i)
        yield


def print_1_to_52():
    for i in range(52):
        print i + 1
        if i == 26 - 1:
            task_manager.add_task(print_A_to_Z())
        yield


task_manager = TaskManager()
task_manager.add_task(print_a_to_z())
task_manager.add_task(print_1_to_52())
task_manager.run()
