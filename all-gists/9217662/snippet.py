class SchedulerImplementationTestBase(object):
    @pytest.fixture
    def scheduler(self, request):
        sched = self.create_scheduler()
        request.addfinalizer(lambda: self.finish(sched))
        return sched

    def create_scheduler(self):
        raise NotImplementedError

    def create_event(self):
        return Event()

    def process_events(self):
        pass

    def finish(self, sched):
        pass

    def test_scheduler_implementation(self, scheduler):
        """Tests that starting the scheduler eventually calls _process_jobs()."""

        class TimeRoller(object):
            def __init__(self, start, step):
                self.now = start
                self.step = timedelta(seconds=step)

            def next(self):
                return self.now + self.step

            def __call__(self):
                now = self.now
                self.now = self.next()
                return now

        events = []
        vals = [0]
        job_removed_event = self.create_event()
        shutdown_event = self.create_event()
        scheduler._threadpool = DummyThreadPool()

        # Test that pending jobs are added (and if due, executed) when the scheduler starts
        scheduler._current_time = time_roller = TimeRoller(dummy_datetime, 0.2)
        scheduler.add_listener(events.append)
        scheduler.add_listener(lambda e: job_removed_event.set(), EVENT_JOBSTORE_JOB_REMOVED)
        scheduler.add_job(increment, 'date', [time_roller.next()], args=(vals,))
        scheduler.start()
        self.process_events()
        job_removed_event.wait(2)
        assert job_removed_event.is_set()
        assert vals[0] == 1
        assert len(events) == 5
        assert events[0].code == EVENT_JOBSTORE_ADDED
        assert events[1].code == EVENT_JOBSTORE_JOB_ADDED
        assert events[2].code == EVENT_SCHEDULER_START
        assert events[3].code == EVENT_JOB_EXECUTED
        assert events[4].code == EVENT_JOBSTORE_JOB_REMOVED
        del events[:]
        job_removed_event.clear()

        # Test that adding a job causes it to be executed after the specified delay
        job = scheduler.add_job(increment, 'date', [time_roller.next() + time_roller.step * 2], args=(vals,))
        self.process_events()
        sleep(0.5)
        self.process_events()
        job_removed_event.wait(2)
        assert job_removed_event.is_set()
        assert vals[0] == 2
        assert len(events) == 3
        assert events[0].code == EVENT_JOBSTORE_JOB_ADDED
        assert events[1].code == EVENT_JOB_EXECUTED
        assert events[2].code == EVENT_JOBSTORE_JOB_REMOVED
        del events[:]
        job_removed_event.clear()

        # Test that shutting down the scheduler emits the proper event
        scheduler.add_listener(lambda e: shutdown_event.set(), EVENT_SCHEDULER_SHUTDOWN)
        scheduler.shutdown()
        self.process_events()
        shutdown_event.wait(2)
        assert shutdown_event.is_set()
        assert len(events) == 1
        assert events[0].code == EVENT_SCHEDULER_SHUTDOWN


class TestBlockingScheduler(SchedulerImplementationTestBase):
    def create_scheduler(self):
        sched = BlockingScheduler()
        self.thread = Thread(target=sched.start)
        sched.start = self.thread.start
        return sched

    def finish(self, sched):
        self.thread.join()


class TestBackgroundScheduler(SchedulerImplementationTestBase):
    def create_scheduler(self):
        return BackgroundScheduler()


class TestAsyncIOScheduler(SchedulerImplementationTestBase):
    def create_scheduler(self):
        asyncio = pytest.importorskip('apscheduler.schedulers.asyncio')
        sched = asyncio.AsyncIOScheduler()
        self.thread = Thread(target=sched._eventloop.run_forever)
        self.thread.start()
        return sched

    def finish(self, sched):
        sched._eventloop.call_soon_threadsafe(sched._eventloop.stop)
        self.thread.join()


class TestGeventScheduler(SchedulerImplementationTestBase):
    def create_scheduler(self):
        gevent = pytest.importorskip('apscheduler.schedulers.gevent')
        return gevent.GeventScheduler()

    def create_event(self):
        from gevent.event import Event
        return Event()


class TestTornadoScheduler(SchedulerImplementationTestBase):
    def create_scheduler(self):
        tornado = pytest.importorskip('apscheduler.schedulers.tornado')
        sched = tornado.TornadoScheduler()
        self.thread = Thread(target=sched._ioloop.start)
        self.thread.start()
        return sched

    def finish(self, sched):
        sched._ioloop.add_callback(sched._ioloop.stop)
        self.thread.join()


class TestTwistedScheduler(SchedulerImplementationTestBase):
    def create_scheduler(self):
        twisted = pytest.importorskip('apscheduler.schedulers.twisted')
        sched = twisted.TwistedScheduler()
        self.thread = Thread(target=sched._reactor.run, args=(False,))
        self.thread.start()
        return sched

    def finish(self, sched):
        sched._reactor.callFromThread(sched._reactor.stop)
        self.thread.join()


class TestQtScheduler(SchedulerImplementationTestBase):
    def create_scheduler(self):
        qt = pytest.importorskip('apscheduler.schedulers.qt')
        from PySide.QtCore import QCoreApplication
        QCoreApplication([])
        return qt.QtScheduler()

    def process_events(self):
        from PySide.QtCore import QCoreApplication
        QCoreApplication.processEvents()