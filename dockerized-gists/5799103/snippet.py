'''Zookeeper-based Scheduler'''
## Standard Library
import cPickle           # Store dictionary in ZooKeeper
import datetime          # Time delta
import socket            # Hostname
## Third Party
import celery            # Current app
import celery.beat       # Scheduler
import celery.utils.log  # Get logger
import kazoo.client      # ZooKeeper Client Library
import kazoo.exceptions  # Base exceptions

logger = celery.utils.log.get_logger(__name__)
NO_LOCK = 0
OLD_LOCK = 1
NEW_LOCK = 2


class ZookeeperNow(object):
    '''Custom class for getting the catch-up time.'''
    now_node = '/celery_schedule/now'

    def __init__(self, hosts):
        self.hosts = hosts

    def now(self):
        '''Get the catch-up time or current time'''
        client = kazoo.client.KazooClient(hosts=self.hosts)
        client.start(timeout=1)
        if client.exists(self.now_node):
            ret = cPickle.loads(client.get(self.now_node)[0])
        else:
            ret = celery.current_app._get_current_object().now()
        client.stop()
        client.close()
        return ret


class ZookeeperScheduleEntry(celery.beat.ScheduleEntry):
    '''Zookeeper-based Entry class'''
    editable_fields = ('task', 'args', 'kwargs', 'options')
    volatile_fields = ('last_run_at', 'total_run_count')

    def __init__(self, hosts, **kwargs):
        super(ZookeeperScheduleEntry, self).__init__(**kwargs)
        self.hosts = hosts
        zk_now = ZookeeperNow(hosts)
        self.schedule.nowfun = zk_now.now
        self.client = kazoo.client.KazooClient(hosts=hosts)
        self.update_zookeeper()

    def __iter__(self):
        return (x for x in vars(self).items() if x[0] != 'client')

    def delete(self):
        '''Delete a node from the schedule entries.'''
        node = '/celery_schedule/entries/%s' % self.name
        self.client.start()
        if self.client.exists(node):
            self.client.delete(node, recursive=True)
        self.client.stop()
        self.client.close()

    def update(self, other):
        if isinstance(other, dict):
            self.__dict__.update(other)
        else:
            self.__dict__.update({'task': other.task, 'options': other.options,
                                  'args': other.args, 'kwargs': other.kwargs,
                                  'schedule': other.schedule})
        self.update_zookeeper()

    def update_zookeeper(self):
        '''Add relevant values to Zookeeper'''
        node = '/celery_schedule/entries/%s' % self.name
        self.client.start()
        if self.client.exists(node):
            stored_values = cPickle.loads(self.client.get(node)[0])
            for key in self.editable_fields:
                stored_values[key] = getattr(self, key)
            for key in (x for x in self.volatile_fields if getattr(self, x)):
                stored_values[key] = getattr(self, key)
            self.client.set(node, cPickle.dumps(stored_values))
        else:
            stored_values = {}
            for key, value in vars(self).iteritems():
                if key in self.editable_fields + self.volatile_fields:
                    stored_values[key] = value
            self.client.create(node, cPickle.dumps(stored_values))
        self.client.stop()
        self.client.close()


class ZookeeperScheduler(celery.beat.Scheduler):
    '''Zookeeper-based Scheduler class'''
    Entry = ZookeeperScheduleEntry
    now_node = '/celery_schedule/now'

    def __init__(self, *args, **kwargs):
        if not kwargs['lazy']:
            self.hosts = kwargs['app'].conf.ZOOKEEPER_HOSTS
            self.client = kazoo.client.KazooClient(hosts=self.hosts)
            self.client.start()
            identifier = socket.gethostname()
            self.lock = self.client.Lock('/celery_schedule/lock', identifier)
            self._has_lock = self.lock.acquire(blocking=False)
            if not self._has_lock:
                self.original_interval = self.max_interval
                self.max_interval = 20
        super(ZookeeperScheduler, self).__init__(*args, **kwargs)

    @property
    def lock_status(self):
        if self._has_lock:
            return OLD_LOCK
        else:
            self._has_lock = self.lock.acquire(blocking=False)
            if self._has_lock:
                self.max_interval = self.original_interval
                return NEW_LOCK
            else:
                return NO_LOCK

    def _catch_up(self):
        '''Cycle through missed scheduled events and run them to catch up due
        to new lockholder.'''
        schedule = self.schedule
        now = celery.current_app._get_current_object().now()
        interval_ts = now - datetime.timedelta(self.max_interval)
        ## Find the last run, going to further back that the max interval. This
        ## check catches us up, but doesn't try to go too far back and possibly
        ## get down time as well as just a dead leader.
        last_runs = [x.last_run_at for x in schedule.itervalues()]
        last_run = max(last_runs + [interval_ts])
        self.client.create(self.now_node, cPickle.dumps(last_run))
        intervals = []
        for entry in schedule.itervalues():
            interval = entry.is_due()[1]
            if interval:
                intervals.append(interval)
        interval = min(intervals + [self.max_interval])
        ## If the time difference between the latest run and the interval
        ## doesn't catch up to current time, the scheduler needs to play
        ## catch up before running normally.
        run_time = last_run + datetime.timedelta(interval)
        now = celery.current_app._get_current_object().now()
        while run_time < now:
            self.client.set(self.now_node, cPickle.dumps(run_time))
            intervals = []
            try:
                for entry in schedule.itervalues():
                    interval = self.maybe_due(entry, self.publisher)
                    if interval:
                        intervals.append(interval)
            except RuntimeError:
                pass
            interval = min(intervals + [self.max_interval])
            run_time += datetime.timedelta(interval)
            now = celery.current_app._get_current_object().now()
        self.client.delete(self.now_node)

    def tick(self):
        lock_status = self.lock_status
        if lock_status:
            if lock_status == NEW_LOCK:
                ## Since the system could have been down, we need to play catch
                ## up since the last run.
                self._catch_up()
            remaining_times = []
            try:
                for entry in self.schedule.itervalues():
                    next_time_to_run = self.maybe_due(entry, self.publisher)
                    if next_time_to_run:
                        remaining_times.append(next_time_to_run)
            except RuntimeError:
                pass
            return min(remaining_times + [self.max_interval])
        else:
            ## If we don't control the lock, sleep until the next interval and
            ## see if we get the lock.
            logger.debug('Lock not held. Sleeping max interval.')
            return self.max_interval

    def setup_schedule(self):
        '''Setup the schedule and store in Zookeeper.'''
        self.update_schedule(self.app.conf.CELERYBEAT_SCHEDULE)
        self.install_default_entries(self.schedule)

    def update_schedule(self, b):
        '''Update the schedule, adding new and removing old entries.'''
        schedule = self.schedule
        A, B = set(schedule), set(b)

        # Remove items from disk not in the schedule anymore.
        for key in A ^ B:
            entry = schedule.pop(key, None)
            if entry:
                entry.delete()

        # Update and add new items in the schedule
        for key in B:
            entry = self.Entry(hosts=self.hosts, **dict(b[key], name=key))
            if schedule.get(key):
                schedule[key].update(entry)
            else:
                schedule[key] = entry

    def _maybe_entry(self, name, entry):
        if isinstance(entry, self.Entry):
            return entry
        return self.Entry(hosts=self.hosts, **dict(entry, name=name))

    @property
    def schedule(self):
        '''Get the schedule entries, updating from Zookeeper.'''
        entries_node = '/celery_schedule/entries'
        self.client.ensure_path(entries_node)
        for entry in self.data:
            entry_node = '{}/{}'.format(entries_node, entry)
            data = cPickle.loads(self.client.get(entry_node)[0])
            self.data[entry].update(data)
        return self.data

    def close(self):
        self.lock.release()
        try:
            self.client.stop()
        except:
            pass
        try:
            self.client.close()
        except:
            pass
