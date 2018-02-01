#!/usr/bin/python3
import os
import cgi
import cgitb
cgitb.enable()
import subprocess
import urllib.request

form = cgi.FieldStorage()
source = form.getvalue('source', None)
target = form.getvalue('target', None)
server = os.environ.get('SERVER_NAME', None)
method = os.environ.get('REQUEST_METHOD', 'GET')


def validate(source, target, server, method, callback_if_valid):
    status = 400
    if method != 'POST':
        message = 'Webmention MUST be performed through a POST request.'
    elif source is None or target is None:
        message = 'Please fill in the source and target fields.'
    elif '://' not in source or '://' not in target:
        message = 'Source and target fields should be URLs.'
    elif not target.split('://', 1)[1].startswith(server):
        message = 'Target should be a link to this domain: {0}'.format(server)
    elif not target in urllib.request.urlopen(source).read().decode('utf-8'):
        message = 'Source should have a link to the target: {0}'.format(target)
    else:
        message = 'Success! With source={source} and target={target}'.format(
            source=source,
            target=target,
        )
        status = 202
        callback_if_valid(source, target)
    return status, message


def send_response(status, message):
    print('Content-type: text/html')
    print('Status: {0}'.format(status))
    print()
    print("""<!doctype html><html lang=en>
    <head><meta charset=utf-8><title>Webmention</title></head>
    <body><p>{message}</p></body></html>""".format(message=message))


def on_valid_submission(source, target):
    commands = [
        'cd /home/larlet/www',
        'source /home/larlet/.virtualenvs/webmention/bin/activate',
        'fab --hide=everything add_webmention:{source},{target}'.format(
            source=source,
            target=target,
        ),
    ]
    subprocess.call(' && '.join(commands), shell=True)


send_response(*validate(source, target, server, method, on_valid_submission))
