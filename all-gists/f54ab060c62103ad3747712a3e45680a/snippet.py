import emoji
import schedule
import asyncio
import inspect

from datetime import datetime


class Job(schedule.Job):

    async def run(self):
        if (inspect.iscoroutine(self.job_func.func)
            or inspect.iscoroutinefunction(self.job_func.func)):
            ret = await self.job_func()
        else:
            ret = self.job_func()


class Scheduler(schedule.Scheduler):

    async def run_pending(self):
        runnable_jobs = (job for job in self.jobs if job.should_run)

        for job in sorted(runnable_jobs):
            ret = await job.run()

            if isinstance(ret, schedule.CancelJob) or ret is schedule.CancelJob:
                self.cancel_job(job)

    def every(self, interval=1):
        job = Job(interval)
        self.jobs.append(job)
        return job


async def show_me_emoji(emoji, count=10):
    print(' '.join(emoji * count))
    

def print_sync(message='this is a sync function'):
    print(message)


async def run_scheduler(scheduler):
    while True:
        await scheduler.run_pending()
        await asyncio.sleep(1)


if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    sch = Scheduler()

    sch.every(5).seconds.do(show_me_emoji, '🐍')
    sch.every(5).seconds.do(print_sync)
    sch.every(5).seconds.do(show_me_emoji, '🍺🍹🍷🍸', 3)
    sch.every(5).seconds.do(print_sync, 'can you believe it')
    sch.every(5).seconds.do(show_me_emoji, '💥')

    loop.run_until_complete(run_scheduler(sch))