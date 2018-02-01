import flask
from flask.ext.classy import FlaskView, route
from functools import wraps

def charset_utf8(viewmethod):
    # Let's update the 'Content-Type' in the HTTP header to tell the browser that the data we're 
    # responding with has utf-8 character encoding.
    @wraps(viewmethod)
    def new_viewmethod(*args, **kwargs):
        resp = viewmethod(*args, **kwargs)
        resp.headers['Content-Type'] += ';charset=utf-8'
        return resp
    return new_viewmethod

# Then you'd do something like...

class JSON(FlaskView):
    route_base = '/json/'
    
    @route('query/<int:id>/', methods=["GET"])
    @charset_utf8 # using our cool new decorator
    def query_by_id(self, id):
        res = solr_connection_or_whatever.search("id:%d" % id)
        response = flask.jsonify(**res)
        return response