import json
from functools import wraps
from flask import redirect, request, current_app

def support_jsonp(f):
    """Wraps JSONified output for JSONP"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            content = str(callback) + '(' + str(f().data) + ')'
            return current_app.response_class(content, mimetype='application/json')
        else:
            return f(*args, **kwargs)
    return decorated_function

# then in your view
@default.route('/test', methods=['GET'])
@support_jsonp
def test():
    return jsonify({"foo":"bar"})