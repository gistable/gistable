# -*- coding: utf-8 -*-
import json
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/echo", methods=['GET', 'POST'])
def echo():
    try:
        json_obj = request.get_json()
        print(json_obj)
        return json.dumps(json_obj)
    except Exception as e:
        return jsonify(message=e)


if __name__ == "__main__":
    app.run()