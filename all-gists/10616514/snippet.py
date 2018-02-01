""":mod:`crontab` --- Quick-and-dirty linux crontab-like event scheduler.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can schedule tasks like this::

    import datetime

    import crontab

    def o_clock():
        print 'Hour:', datetime.datetime.now().hour

    def keep_alive():
        print send_ping()

    # Create crontab runner
    cron = crontab.ThreadCronTab([
        crontab.Event(o_clock, minutes=0),  # For 0 minute of every hours
        crontab.every(keep_alive, minutes=1),  # Every 1 minutes
    ])

    @cron.every(minutes=1)
    def check_config():
        if is_changed('config.ini'):
            parse_config('config.ini')

    # Run crontab
    crontab.run()

"""
import time
import Queue
import numbers
import datetime
import threading

__all__ = ('CronTab', 'Event', 'every', 'ThreadCronTab')


def to_set(item):
    """Convert to set.
    """
    if isinstance(item, set):
        return item
    if isinstance(item, numbers.Integral):
        return {item}  # Single item
    return set(item) if item else {}


class Event(object):
    """Event class::

        def function():
            print 'Do something'

        event1 = Event(function, minutes=0)
        event2 = Event(function, name='by_hour', hours=(1, 2, 3))

        crontab.add_event(event1)
        crontab.add_event(event2)

        ...


    """
    def __init__(self, action, name=None, minutes=None, hours=None, days=None,
                 months=None, weekdays=None, args=None, kwargs=None):
        self.action = action
        self.name = name or action.__name__

        self.minutes = to_set(minutes)
        self.hours = to_set(hours)
        self.days = to_set(days)
        self.months = to_set(months)
        self.weekdays = to_set(weekdays)

        self.args = args or ()
        self.kwargs = kwargs or {}

        self.last_exec_time = None

    def __call__(self):
        return self.action(*self.args, **self.kwargs)

    def __repr__(self):
        s = '<@event: %s' % self.name
        li = []

        if self.minutes:
            li.append('minutes=(' + ', '.join(map(str, self.minutes)) + ')')

        if self.hours:
            li.append('hours=(' + ', '.join(map(str, self.hours)) + ')')

        if self.days:
            li.append('days=(' + ', '.join(map(str, self.days)) + ')')

        if self.months:
            li.append('months=(' + ', '.join(map(str, self.months)) + ')')

        if self.weekdays:
            li.append('weekdays=(' + ', '.join(map(str, self.weekdays)) + ')')

        if li:
            s += ', '
            s += ', '.join(li)

        return s + '>'

    def executable_time(self, current):
        """Returns executable time tuple for time `current`

        :returns: caculated executable time if acceptable or :const:`None`.

        """
        minute = 0
        hour = 0
        day = 1
        month = 1
        weekday = 0

        if any((collection) and (not item in collection)
               for collection, item in
               [
                   (self.minutes, current.minute),
                   (self.hours, current.hour),
                   (self.days, current.day),
                   (self.months, current.month),
                   (self.weekdays, current.weekday()),
               ]):
            return None

        f = lambda item, collection, default: item if collection else default

        minute = f(current.minute, self.minutes, minute)
        hour = f(current.hour, self.hours, hour)
        day = f(current.day, self.days, day)
        month = f(current.month, self.months, month)
        weekday = f(current.weekday(), self.weekdays, weekday)

        return (minute, hour, day, month, weekday)


def every(action, months=None, days=None, hours=None, minutes=None,
          args=None, kwargs=None):
    """Every N minute, hours, days, months...
    """
    if months:
        days = range(1, 12 + 2, months)

    if days:
        days = range(1, 31 + 1, days)

    if hours:
        hours = range(0, 24, hours)

    if minutes:
        minutes = range(0, 60, minutes)

    return Event(
        action,
        # The number `0` is not allowed.
        months=months or None,
        days=days or None,
        hours=hours or None,
        minutes=minutes or None,
    )


class CronTab(object):
    """Simple linux crontab-like event scheduler.
    """
    def __init__(self, events=(),
                 sleep_function=time.sleep,
                 datetime_type=datetime.datetime,
                 timedelta_type=datetime.timedelta,
                 now_fuction=None):
        self.interval = 30  # in seconds
        self.events = list(events)  # Copy
        self.sleep_function = sleep_function
        self.datetime_type = datetime_type
        self.timedelta_type = timedelta_type
        self.now_function = now_fuction or datetime_type.now
        self.cancelled = False

    def spawn(self, event):
        """Execute task
        """
        raise NotImplementedError('Subclass this class and implement `spawn`')

    def run(self):
        now = self.now_function()
        to_time = self.datetime_type(*now.timetuple()[:5])
        while not self.cancelled:
            for event in self.events:
                exec_time = event.executable_time(now)
                if exec_time and exec_time != event.last_exec_time:
                    event.last_exec_time = exec_time
                    self.spawn(event)

            to_time += self.timedelta_type(seconds=self.interval)

            now = self.now_function()
            while now < to_time:
                self.sleep_function((to_time - now).seconds)
                now = self.now_function()

    def add_event(self, event):
        self.events.append(event)

    def event(self, **kwargs):
        """Decorator-based event generator.

        :param \*\*kwargs: kwargs to :class:`Event` after `action`.

        """
        def decorator(fn):
            event = Event(fn, **kwargs)
            self.add_event(event)
            return event
        return decorator

    def every(self, **kwargs):
        """Decorator-based every event generator.

        :param \*\*kwargs: kwargs to :func:`every` after `action`.

        """
        def decorator(fn):
            event = every(fn, **kwargs)
            self.add_event(event)
            return event
        return decorator


class ThreadCronTab(CronTab):
    """Thread-based crontab runner.
    """
    def __init__(self, *args, **kwargs):
        super(ThreadCronTab, self).__init__(*args, **kwargs)
        self.queue = Queue.Queue()
        self.thread = threading.Thread(target=self.loop)
        self.thread.daemon = True

    def loop(self):
        """Thread loop
        """
        while not self.cancelled:
            try:
                event = self.queue.get(timeout=self.interval)
            except Queue.Empty:
                pass
            else:
                event()

    def spawn(self, event):
        self.queue.put(event)

    def run(self):
        self.thread.start()
        super(ThreadCronTab, self).run()
