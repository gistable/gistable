from flask import abort, make_response, jsonify
abort(make_response(jsonify(message="Message goes here"), 400))