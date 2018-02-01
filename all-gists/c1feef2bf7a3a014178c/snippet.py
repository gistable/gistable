'''

testing celery progress reporting/polling


* start server
python tempserver.py

* start worker
celery -A tempserver worker -c 1 --loglevel=DEBUG

* browse to localhost:5000/
'''

from flask import Flask, \
        request, redirect, flash, \
        url_for, session, g, \
        render_template, render_template_string
from flask import Blueprint

REDIS_SERVER_URL = 'localhost'
CELERY_BROKER_HOST = 'redis://%s:6379' % (REDIS_SERVER_URL)

from celery import Celery, current_task
from celery.result import AsyncResult

import os
celery = Celery(os.path.splitext(__file__)[0],
        backend=CELERY_BROKER_HOST+'/1',
        broker=CELERY_BROKER_HOST+'/1')

import uuid
import random
import time
import json

@celery.task
def slow_proc():
    NTOTAL = 10
    for i in range(NTOTAL):
        time.sleep(random.random())
        current_task.update_state(state='PROGRESS',
                meta={'current':i,'total':NTOTAL})
    return 999



app = Flask(__name__)


@app.route('/progress')
def progress():
    jobid = request.values.get('jobid')
    if jobid:
        # GOTCHA: if you don't pass app=celery here,
        # you get "NotImplementedError: No result backend configured"
        job = AsyncResult(jobid, app=celery)
        print job.state
        print job.result
        if job.state == 'PROGRESS':
            return json.dumps(dict(
                state=job.state,
                progress=job.result['current']*1.0/job.result['total'],
            ))
        elif job.state == 'SUCCESS':
            return json.dumps(dict(
                state=job.state,
                progress=1.0,
            ))
    return '{}'

@app.route('/enqueue')
def enqueue():
    job = slow_proc.delay()
    return render_template_string('''\
<style>
#prog {
width: 400px;
border: 1px solid red;
height: 20px;
}
#bar {
width: 0px;
background-color: blue;
height: 20px;
}
</style>
<h3></h3>
<div id="prog"><div id="bar"></div></div>
<div id="pct"></div>
<script src="//code.jquery.com/jquery-2.1.1.min.js"></script>
<script>
function poll() {
    $.ajax("{{url_for('.progress', jobid=JOBID)}}", {
        dataType: "json"
        , success: function(resp) {
            console.log(resp);
            $("#pct").html(resp.progress);
            $("#bar").css({width: $("#prog").width() * resp.progress});
            if(resp.progress >= 0.9) {
                $("#bar").css({backgroundColor: "green"});
                return;
            } else {
                setTimeout(poll, 1000.0);
            }

        }
    });

}

$(function() {
    var JOBID = "{{ JOBID }}";
    $("h3").html("JOB: " + JOBID);
    poll();

});
</script>
''', JOBID=job.id)


@app.route('/')
def index():
    return render_template_string('''\

<a href="{{ url_for('.enqueue') }}">launch job</a>
''')


if __name__ == '__main__':
    app.run(debug=True)
