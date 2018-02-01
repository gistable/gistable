#!/usr/bin/env python

import os, sys
sys.path.append(os.getcwd())

import logging
import rq

MAX_FAILURES = 3

logger = logging.getLogger(__name__)

queues = None

def retry_handler(job, exc_type, exc_value, traceback):
    job.meta.setdefault('failures', 0)
    job.meta['failures'] += 1

    # Too many failures
    if job.meta['failures'] >= MAX_FAILURES:
        logger.warn('job %s: failed too many times times - moving to failed queue' % job.id)
        job.save()
        return True

    # Requeue job and stop it from being moved into the failed queue
    logger.warn('job %s: failed %d times - retrying' % (job.id, job.meta['failures']))

    for queue in queues:
        if queue.name == job.origin:
            queue.enqueue_job(job, timeout=job.timeout)
            return False

    # Can't find queue, which should basically never happen as we only work jobs that match the given queue names and
    # queues are transient in rq.
    logger.warn('job %s: cannot find queue %s - moving to failed queue' % (job.id, job.origin))
    return True


with rq.Connection():
    queues = map(rq.Queue, sys.argv[1:]) or [rq.Queue()]

    worker = rq.Worker(queues)
    worker.push_exc_handler(retry_handler)
    worker.work()