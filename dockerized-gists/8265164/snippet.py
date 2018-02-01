from bottle import route, run, request, static_file

@route('/')
def serve_index():
  return static_file('index.html', root='')

@route('/assets/<filepath:path>')
def serve_asset(filepath):
  return static_file(filepath, root='assets/')

@route('/js/<filepath:path>')
def serve_js(filepath):
  return static_file(filepath, root='js/')

run(host='localhost', port=8888)
