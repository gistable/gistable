# import dependencies
from functools import wraps
from google.appengine.api import users
from flask import redirect, request

USERS = ["any@gmail.com", "any@googleapps.com"]


#Set's the login to Google Users Service
def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not users.get_current_user():
            return redirect(users.create_login_url(request.url))
        else:
            user = users.get_current_user()
            if user.email() in USERS:
                return func(*args, **kwargs)
            else:
                return 'Trampak iten ?'
    return decorated_view
