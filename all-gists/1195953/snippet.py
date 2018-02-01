from flask import request, make_response,

def any_response(data):
  ALLOWED = ['http://localhost:8888']
  response = make_response(data)
  origin = request.headers['Origin']
  if origin in ALLOWED:
    response.headers['Access-Control-Allow-Origin'] = origin
  return response