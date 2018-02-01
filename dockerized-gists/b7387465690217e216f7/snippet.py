# -*- coding: utf-8 -*-
import pygal
from flask import Flask, Response


app = Flask(__name__)


@app.route('/')
def index():
    """ render svg on html """
    return """
<html>
    <body>
        <h1>hello pygal</h1>
        <figure>
        <embed type="image/svg+xml" src="/graph/" />
        </figure>
    </body>
</html>'
"""


@app.route('/graph/')
def graph():
    """ render svg graph """
    bar_chart = pygal.Bar()
    bar_chart.add('Fibonacci', [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55])
    return Response(response=bar_chart.render(), content_type='image/svg+xml')


if __name__ == '__main__':
    app.run()