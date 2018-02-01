import time

from celery import chord
from celery.utils import uuid

from my_app.celery import celery


class ProgressChord(chord):

    """
    Chord that returns both the callback's AsyncResult and the group's
    AsyncResult.
    """

    # See:
    # http://stackoverflow.com/questions/15441101/how-to-track-the-progress-of-individual-tasks-inside-a-group-which-forms-the-hea
    # https://groups.google.com/forum/?fromgroups=#!topic/celery-users/xSdxI-Z08Cw

    def __call__(self, body=None, **kwargs):
        # Taken from celery source code, celery.canvas
        _chord = self.Chord
        body = (body or self.kwargs['body']).clone()
        kwargs = dict(self.kwargs, body=body, **kwargs)
        if _chord.app.conf.CELERY_ALWAYS_EAGER:
            return self.apply((), kwargs)
        callback_id = body.options.setdefault('task_id', uuid())
        # We store the result
        r = _chord(**kwargs)
        # Printing r here gives something like:
        # <GroupResult: 60ff9ad1-d2d5-4dad-a496-33b2eb85f952 [ed0e155c-5228-4d95-b0aa-1f1ec4aad79d, 23f55076-9a8a-4990-b4b0-b3090e5563b4]>
        return _chord.AsyncResult(callback_id), r


@celery.task
def do_stuff():
    """Do stuff."""
    time.sleep(2)  # expensive function
    return 1 + 1


@celery.task
def manage_results(results):
    """Send an email about the results."""
    send_email(json.dumps(results))


# I'm not including the whole flask boilerplate but let's say the task
# is scheduled by an HTTP call, and we return the task_id.
@app.route("/run_job")
def create_tasks()
    """Create the chord."""

    header = list(do_stuff.si() for i in range(2000))
    body_result, group_result = ProgressChord(group(header))(manage_results.s())

    # We'll use this task_id to retrieve results
    return group_result.id


# Same thing, this is pseudo code. The idea is that the HTTP client is
# passing back the task_id and expects some information about the tasks
# group, including the completed count.
@app.route("/job_status")
def get_job_status(task_id):
    """Return the job completion rate."""

    result = do_stuff.AsyncResult(task_id)
    group_result = result.children[0]

    print group_result.app
    # prints <Celery default:0x109a0c590>
    print group_result.app.backend
    # prints <celery.backends.base.DisabledBackend object at 0x109a20550>

    info = dict(
        completed_count=group_result_set.completed_count()
    )

    return info
