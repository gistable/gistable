
from collections import defaultdict
import concurrent.futures


class TasksGroup(object):
    """A group of tasks with dependencies.

    >>> tasks = TasksGroup()
    >>> @tasks.add()
    ... def first():
    ...     print(1)
    >>> @tasks.add(first)
    ... def second():
    ...     print(2)
    >>> import concurrent.futures
    >>> with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    ...     tasks.run(executor)
    1
    2
    """

    def __init__(self):
        #: Maps functions to their upstream connections (dependencies)
        self._upstream = {}
        #: Maps functions to their downstream connections
        self._downstream = defaultdict(set)

    def add(self, *depends_on):
        """Add a task to the group.
        """
        def decorator(func):
            self._upstream[func] = depends_on
            for f in depends_on:
                self._downstream[f].add(func)
            return func

        return decorator

    def run(self, executor):
        """Run tasks respecting the dependencies using an executor.
        """
        count_deps = {task: len(deps) for task, deps in self._upstream.items()}
        base_tasks = {task for task, count in count_deps.items() if count == 0}

        future_to_task = {executor.submit(task): task for task in base_tasks}
        not_done = set(future_to_task.keys())

        wait = concurrent.futures.wait
        FIRST_COMPLETED = concurrent.futures.FIRST_COMPLETED
        while not_done:
            done, not_done = wait(not_done, return_when=FIRST_COMPLETED)
            for future in done:
                task = future_to_task[future]
                for f in self._downstream[task]:
                    count_deps[f] -= 1
                    if count_deps[f] == 0:
                        fut = executor.submit(f)
                        future_to_task[fut] = f
                        not_done.add(fut)



# Example

import time
tasks = TasksGroup()

@tasks.add()
def f1():
    time.sleep(.4)
    print(time.time(), 1)

@tasks.add(f1)
def f2():
    time.sleep(4)
    print(time.time(), 2)

@tasks.add(f1)
def f3():
    time.sleep(.4)
    print(time.time(), 3)

@tasks.add(f3)
def f4():
    time.sleep(.4)
    print(time.time(), 4)


with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    tasks.run(executor)
