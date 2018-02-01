from flask import Flask, jsonify, Blueprint, current_app
import json

## REST api ###################################################################

api = Blueprint('api', __name__)

@api.route("/users")
def users():
    return jsonify(users=[
        {"username": "alice", "user_id": 1},
        {"username": "bob", "user_id": 2},
    ])

## app ########################################################################

app = Flask(__name__)
app.config["DEBUG"] = True
app.register_blueprint(api, url_prefix="/v1")

def get_json_response(view_name, *args, **kwargs):
    '''Calls internal view method, parses json, and returns python dict.'''
    view = current_app.view_functions[view_name]
    res = view(*args, **kwargs)
    #XXX: to avoid the json decode internally for every call,
    #you could make your own jsonify function that used a subclass
    #of Response which has an attribute with the underlying
    #(non-JSON encoded) data
    js = json.loads(res.data)
    return js

@app.route("/")
def index():
    js = get_json_response('api.users')
    usernames = [u['username'] for u in js['users']]
    return "<h1>Hello</h1><p>Users are: %r</p>" % usernames #XXX: render a template here

###############################################################################

if __name__ == "__main__":
    app.run(use_debugger=True, use_reloader=True)