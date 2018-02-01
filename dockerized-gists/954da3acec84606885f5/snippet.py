import datetime
import time
from functools import wraps
from wsgiref.handlers import format_date_time
from flask import make_response


def cache(expires=None, round_to_minute=False):
    """
    Add Flask cache response headers based on expires in seconds.
    
    If expires is None, caching will be disabled.
    Otherwise, caching headers are set to expire in now + expires seconds

    If round_to_minute is True, then it will always expire at the start of a minute (seconds = 0)
    
    Example usage:
    
    @app.route('/map')
    @cache(expires=60)
    def index():
      return render_template('index.html')
    
    """
    def cache_decorator(view):
        @wraps(view)
        def cache_func(*args, **kwargs):
            now = datetime.datetime.now()
 
            response = make_response(view(*args, **kwargs))
            response.headers['Last-Modified'] = format_date_time(time.mktime(now.timetuple()))
            
            if expires is None:
                response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
                response.headers['Expires'] = '-1'
            else:
                expires_time = now + datetime.timedelta(seconds=expires)

                if round_to_minute:
                    expires_time = expires_time.replace(second=0, microsecond=0)

                response.headers['Cache-Control'] = 'public'
                response.headers['Expires'] = format_date_time(time.mktime(expires_time.timetuple()))
 
            return response
        return cache_func
    return cache_decorator