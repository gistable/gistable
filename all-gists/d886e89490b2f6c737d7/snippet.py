from __future__ import absolute_import

import signal
import gevent
import gevent.pool
from rq import Worker
from rq.timeouts import BaseDeathPenalty, JobTimeoutException
from rq.worker import StopRequested, green, blue
from rq.exceptions import DequeueTimeout


class GeventDeathPenalty(BaseDeathPenalty):
    def setup_death_penalty(self):
        exception = JobTimeoutException('Gevent Job exceeded maximum timeout value (%d seconds).' % self._timeout)
        self.gevent_timeout = gevent.Timeout(self._timeout, exception)
        self.gevent_timeout.start()

    def cancel_death_penalty(self):
        self.gevent_timeout.cancel()


class GeventWorker(Worker):
    death_penalty_class = GeventDeathPenalty

    def __init__(self, *args, **kwargs):
        pool_size = 20
        if 'pool_size' in kwargs:
            pool_size = kwargs.pop('pool_size')
        self.gevent_pool = gevent.pool.Pool(pool_size)
        super(GeventWorker, self).__init__(*args, **kwargs)

    def get_ident(self):
        return id(gevent.getcurrent())

    def _install_signal_handlers(self):
        def request_force_stop():
            self.log.warning('Cold shut down.')
            self.gevent_pool.kill()
            raise SystemExit()

        def request_stop():
            if not self._stopped:
                gevent.signal(signal.SIGINT, request_force_stop)
                gevent.signal(signal.SIGTERM, request_force_stop)

                self.log.warning('Warm shut down requested.')
                self.log.warning('Stopping after all greenlets are finished. '
                                 'Press Ctrl+C again for a cold shutdown.')

                self._stopped = True
                self.gevent_pool.join()

        gevent.signal(signal.SIGINT, request_stop)
        gevent.signal(signal.SIGTERM, request_stop)

    def execute_job(self, job):
        self.gevent_pool.spawn(self.perform_job, job)

    def dequeue_job_and_maintain_ttl(self, timeout):
        if self._stopped:
            raise StopRequested()

        result = None
        while True:
            if self._stopped:
                raise StopRequested()

            self.heartbeat()

            while self.gevent_pool.full():
                gevent.sleep(0.1)
                if self._stopped:
                    raise StopRequested()

            try:
                result = self.queue_class.dequeue_any(self.queues, 5, connection=self.connection)
                if result is None and timeout is None:
                    self.gevent_pool.join()
                if result is not None:
                    job, queue = result
                    self.log.info('%s: %s (%s)' % (green(queue.name),
                                  blue(job.description), job.id))
                break
            except DequeueTimeout:
                pass

        self.heartbeat()
        return result