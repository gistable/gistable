
"""
Celery tasks that batch a job with many tasks into smaller work sets.

The problem I'm attempting to solve is one where a job comprised of many
tasks (say 100) will snub out a job comprised of only a few tasks (say 5).  It
appears as though by default celery will queue up the second job's 5 tasks 
behind the first job's 100 and it will have to wait until the first job's 
completion before it even begins.

This prototype code shows how jobs can be batched into smaller task sizes in 
order to prevent a massive job from taking over all processing resources.

Caveat: as the code is written, a job will not detect a subtask erroring out
and will continue processing the job to completion.  This may or may not be
desired.
"""
import os
import random
import time

from logging import info

from celery.task import chord, task
from celery.task.sets import TaskSet

WORK_DIR = '/tmp/work_done' # where work goes

# this number should be chosen relative to the number of workers in the pool so
# that multiple jobs coming into the system don't have to wait too long to
# start processing.  making this number low leaves idle resources when there
# are no additional jobs, but making it too high, adds a start penalty to any
# job entering the system.
ITEMS_PER_BATCH = 5

@task
def prep_job(job_id, num_tasks):
    """
    Prepare by creating sets of tasks each made up of <ITEMS_PER_BATCH> items
    """

    # create a list of numbers that represent jobs
    numbers = range(num_tasks)

    # a list of lists representing the jobs in batches
    batches = get_batches(numbers, ITEMS_PER_BATCH)

    # calling job_dispatch will start processing the jobs one batch at a time
    return job_dispatch.delay(None, job_id, batches)

@task
def job_dispatch(results, job_id, batches):
    """
    Process the job batches one at a time

    When there is more than one batch to process, a chord is used to delay the
    execution of remaining batches.
    """

    batch = batches.pop(0)

    info('dispatching job_id: {0}, batch: {1}, results: {2}'.format(job_id, batch, results))

    tasks = [job_worker.subtask((job_id, task_num)) for task_num in batch]

    # when there are other batches to process, use a chord to delay the
    # execution of remaining tasks, otherwise, finish off with a TaskSet
    if batches:
        info('still have batches, chording {0}'.format(batches))
        callback = job_dispatch.subtask((job_id, batches))
        return chord(tasks)(callback)
    else:
        info('only batch, calling TaskSet')
        return TaskSet(tasks=tasks).apply_async()

@task
def job_worker(job_id, task_num):
    return do_the_work(job_id, task_num)

#
# Helper methods
#

def get_batches(work, batch_size):
    batches = []

    while work:
        t_batch_size = min(len(work), batch_size)

        batches.append(work[:t_batch_size])
        work = work[t_batch_size:]

    return batches

def do_the_work(job_id, task_num):
    """
    Example of some work unit that will take some time within 2s to complete.

    It writes to the WORK_DIR directory to demonstrate (by listing the
    directory) that other jobs are able to interleave their tasks with another big
    job.
    """

    sleep_time = random.random() * 2

    # fail every once in a while to see if the entire job is shorted after a
    # failure.
    if sleep_time < 0.2:
        raise Exception('misc failure')

    info('job_worker, sleeping {0}'.format(sleep_time))
    time.sleep(sleep_time)

    now = time.time()

    # try/except just in case another worker got to creating the directory
    # first.
    try:
        if not os.path.exists(WORK_DIR):
            os.makedirs(WORK_DIR)
    except OSError, exc:
        if exc[0] != 17:
            raise

    path = os.path.join(WORK_DIR, '{0}-{1}-{2}.txt'.format(now, job_id, task_num))

    info('touching {0}'.format(path))
    open(path, 'wb').close()

    return path
