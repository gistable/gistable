# Context manager to generate batches in the background via a process pool
# Usage:
#
# def batch(seed):
#    .... # generate minibatch
#    return minibatch
#
# with BatchGenCM(batch) as bg:
#    minibatch = next(bg)
#    .... # do something with minibatch

import uuid
import os
import pickle
import hashlib
import numpy as np
from multiprocessing import Process, Queue


class BatchGenCM:
    def __init__(self, batch_fn, seed=None, num_workers=8):
        self.batch_fn = batch_fn
        self.num_workers = num_workers
        if seed is None:
            seed = np.random.randint(4294967295)
        self.seed = str(seed)
        self.id = uuid.uuid4()

    def __enter__(self):
        self.jobq = Queue(maxsize=self.num_workers)
        self.doneq = Queue()
        self.processes = []
        self.current_batch = 0
        self.finished_batches = []

        def produce():
            while True:
                n = self.jobq.get()
                if n is None:
                    break
                seed = hashlib.md5(self.seed + str(n)).hexdigest()
                seed = int(seed, 16) % 4294967295
                batch = self.batch_fn(seed)
                with open('/run/shm/{}-{}'.format(self.id, n), 'w') as ofile:
                    pickle.dump(batch, ofile, protocol=pickle.HIGHEST_PROTOCOL)
                self.doneq.put(n)

        for i in range(self.num_workers):
            self.jobq.put(i)

            p = Process(target=produce)
            self.processes.append(p)
            p.start()

        return self

    def __iter__(self):
        return self

    def next(self):
        n = self.current_batch
        while n not in self.finished_batches:
            i = self.doneq.get()
            self.finished_batches.append(i)

        fn = '/run/shm/{}-{}'.format(self.id, n)
        batch = pickle.load(open(fn))
        os.system('rm {}'.format(fn))

        self.jobq.put(n + self.num_workers)
        self.current_batch += 1
        return batch

    def __exit__(self, exc_type, exc_value, traceback):
        for _ in range(self.num_workers):
            self.jobq.put(None)
        for process in self.processes:
            process.join()
        while not self.doneq.empty():
            _ = next(self)
