from myproject.config import celery_app # Change this.
import requests
import librato
import time
import os

LIBRATO_USERNAME = ""
LIBRATO_API_TOKEN = ""
RABBIT_MQ_API_URL "http://localhost:15672/api/"
RABBIT_MQ_USERNAME = ""
RABBIT_MQ_PASSWORD = ""


def get_workers_current_pool():
    '''
    Get a dictionary of queues with their current workers and concurrency count.
    test = {
        'email': {
            'celery@email.ip-123-123-1': 10,
            'celery@email.ip-182-132-1': 1,
        }
    }
        'celery': {
            ...
        }
    }
    '''
    workers = {}
    stats = celery_app.control.inspect().stats()
    for name, stat in stats.items():
        queue = name.split('@')[1].split('.')[0]
        workers[queue] = workers.get(queue, {})
        workers[queue][name] = len(stat.get('pool').get('processes'))
    return workers


def get_workers_tasks_count():
    '''
    Return a dictonary of the queues with their current task length.
    {
        'email':  170000,
        'celery': 0,
    }
    '''
    lengths = {}
    url = RABBIT_MQ_API_URL, + 'queues/
    response = requests.get(url, auth=(RABBIT_MQ_USERNAME, RABBIT_MQ_PASSWORD))
    data = response.json()

    ignored_names = ['celery@', 'celeryev', 'pidbox']

    for queue in data:
        name = queue.get('name')
        if not any(ignored in name for ignored in ignored_names):
            length = queue.get('backing_queue_status', {}).get('len')
            lengths[name] = length
    return lengths


if __name__ == "__main__":
    """
    Update Librato with our task length per queue and pools per queue.
    """
    while True:
        api = librato.connect(LIBRATO_USERNAME, LIBRATO_API_TOKEN)
        queue = api.new_queue()
        tasks = get_workers_tasks_count()
        pools = get_workers_current_pool()
        for name, count in tasks.iteritems():
            queue.add('%s-tasks' % name, count)
        for name, pool in pools.iteritems():
            queue.add('%s-pools' % name, sum(pool.values())

        queue.submit()
        time.sleep(60)
