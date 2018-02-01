"""
This module provides a simple WSGI profiler middleware for finding 
bottlenecks in web application. It uses the profile or cProfile 
module to do the profiling and writes the stats to the stream provided

To use, run `flask_profiler.py` instead of `app.py`

see: http://werkzeug.pocoo.org/docs/0.9/contrib/profiler/
and: http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvi-debugging-testing-and-profiling
"""

from werkzeug.contrib.profiler import ProfilerMiddleware
from app import app

app.config['PROFILE'] = True
app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions = [30])
app.run(debug = True)