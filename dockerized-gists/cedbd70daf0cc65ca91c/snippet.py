# -*- coding: utf-8 -*-
from functools import wraps

from flask import request


def remove_request_cookies(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        request.environ.pop('HTTP_COOKIE', '')
        return func(*args, **kwargs)
    return wrapper