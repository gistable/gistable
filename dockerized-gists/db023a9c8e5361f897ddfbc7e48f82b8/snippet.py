#!/usr/bin/env python
from flask import Flask, request, abort, jsonify
app = Flask(__name__)

@app.route('/push', methods=['POST'])
def handle_push():
    if not request.json:
        abort(400)
    if 'AnsibleTower' in request.headers and request.headers['AnsibleTower'] == 'xSecretx':
        # Trigger some other external action
        print("Request dictionary: {}".format(request.json))
        return jsonify({'status': 'triggered'}), 201
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    print("Listening...")
    app.run(debug=True, host='0.0.0.0', port=8085)