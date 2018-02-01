
def get_last_run(task_name):
    task = db.scheduled_tasks.find_one({'name': task_name})
    if task is None:
        last_run = time.time()
        # race condition possible, but this only happens at first run
        db.scheduled_tasks.update(
            {
                'name': task_name
            },
            {
                '$set': {
                    'last_run': last_run,
                    'runner': 'none'
                }
            },
            upsert=True
        )
        return datetime.datetime.utcfromtimestamp(last_run)
    return datetime.datetime.utcfromtimestamp(task['last_run'])

def update_last_run(task_name, previous_last_run, new_last_run):
    previous_last_run = (previous_last_run - datetime.datetime(1970, 1, 1)).total_seconds()
    new_last_run = (new_last_run - datetime.datetime(1970, 1, 1)).total_seconds()
    result = db.scheduled_tasks.update(
        {
            'name': task_name,
            'last_run': previous_last_run
        },
        {
            '$set': {
                'last_run': new_last_run,
                'runner': gethostname()
            }
        }
    )
    return result['n'] == 1

class SingleRunScheduler(PersistentScheduler):
    """
    A scheduler that checks a shared store (mongo) to see if any other beat servers sent the task before
    sending it.
    """
    def maybe_due(self, entry, publisher=None):

        entry.last_run_at = get_last_run(entry.name)

        is_due, next_time_to_run = entry.is_due()

        if is_due:
            if update_last_run(entry.name, entry.last_run_at, self.app.now()):
                LOG.info('Scheduler: Sending due task %s (%s)', entry.name, entry.task)
                try:
                    result = self.apply_async(entry, publisher=publisher)
                except Exception, exc:
                    LOG.error('Message Error: %s\n%s',
                        exc, traceback.format_stack(), exc_info=True)
                else:
                    LOG.debug('%s sent. id->%s', entry.task, result.id)
            else:
                LOG.info('Skipping task kick-off: %s took care of it.' % db.scheduled_tasks.find_one({'name': entry.name})['runner'])
                entry = self.reserve(entry)
                _, next_time_to_run = entry.is_due()
        return next_time_to_run

    def reserve(self, entry):
        new_entry = self.schedule[entry.name] = entry.next(get_last_run(entry.name))
        return new_entry
        
        
...

celery.conf.CELERYBEAT_SCHEDULER = "schedulers.SingleRunScheduler"


