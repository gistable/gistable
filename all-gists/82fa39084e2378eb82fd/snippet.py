import json
from urllib import urlencode

from flask import Flask, request, jsonify


app = Flask(__name__)
app.debug = True


def _raise_for_status(r):
    if r.status_code != 200:
        raise ValueError('Bad OLAF request ({}):\n{}'.format(
            r.status, r.get_data()))


def _get(path, params=None):
    if params:
        path += '?' + urlencode(params)
    with app.test_client() as client:
        r = client.get(path)
        _raise_for_status(r)
        return json.loads(r.get_data())


def _post(path, data=None):
    with app.test_client() as client:
        r = client.post(path, data=json.dumps(data),
                        content_type='application/json')
        _raise_for_status(r)
        return json.loads(r.get_data())


@app.route('/')
def index():
    q = request.values.get('q', '')
    return jsonify({
        'message': 'Your data: {} ({})'.format(q, type(q)),
    })


@app.route('/s', methods=['POST'])
def submit():
    v = request.form.get('v', '')
    return jsonify({
        'type': str(type(v)),
        'value': v,
    })


@app.route('/e', methods=['GET', 'POST'])
def echo():
    data = (request.get_json()
            if request.method == 'POST'
            else request.args.to_dict())
    print
    print request.method, 'echo =', data
    return jsonify({'data': data})


print _get('/e', {'a': 1, 'q': 2})
print _get('/e', {'a': 1, 'q': {'b': 2, 'c': 3}})
print _post('/e', {'a': 1, 'v': {'b': 2, 'c': 3}})
