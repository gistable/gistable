from multiprocessing import Pool, Process, Queue

class Multiplexer(object):
    def __init__(self, _map, _reduce, threads=8):
        self._map=_map
        self._reduce=_reduce
        self.consumer=Process(target=self.consume)
        self.pool = Pool(threads)   # reduce if less aggressive
        self.q=Queue()
        self.done=False

    def start(self, ):
        self.done=False
        self.consumer.start()

    def addjob(self, job):
        try:
            self.pool.apply_async(self._map,[job],callback=self.q.put)
        except:
            logger.error('[!] failed to process %s' % job)
            traceback.print_exc(file=sys.stderr)
            raise

    def finish(self, ):
        self.done=True
        self.pool.close()
        self.pool.join()
        self.consumer.join()

    def consume(self, ):
        while not self.done or not self.q.empty():
            self._reduce(self.q.get(True), added, updated)
