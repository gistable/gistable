from bottle import route, run
import subprocess, socket, os, glob

base_path = '/home/minecraft/'

def get_pipe(command):
  return subprocess.Popen(command.split(), stdout=subprocess.PIPE).stdout

def validate_name(name):
  return name and name.isalnum() and ' ' not in name

def jar_in_path(path):
  if not os.path.exists(path):
    return False
  return glob.glob(path + '/*.jar')  

@route('/list/')
def list_servers():
    pipe = get_pipe('mark2 list')
    servers = []
    for line in pipe.readlines():
      if line:
        servers.append(line.rstrip())
    return {'servers': servers}

@route('/hostname/')
def hostname():
    return {'hostname': socket.gethostname()}

@route('/send/<name>/<cmd>')
def send_to_server(name='', cmd =''):
    if not validate_name(name):
      status = 'invalid'
    elif not cmd:
      status = 'invalid'
    elif name not in list_servers()['servers']:
      status = 'invalid'
    else:
      get_pipe('mark2 send -n ' + name + ' ' + cmd)
      status = 'success'
    return {'status': status}

@route('/stop/<name>')
def stop_server(name=''):
    return send_to_server(name, '~stop')

@route('/start/<name>')
def start_server(name=''):
    path = base_path + name
    if not validate_name(name):
      status = 'invalid'
    elif not jar_in_path(path):
      status = 'invalid'
    elif name in list_servers()['servers']:
      status = 'already_started'
    else:
      get_pipe('mark2 start ' + base_path + name)
      status = 'success'
    return {'status': status}

run(host='localhost', port=8080, autojson=True, debug=True)
