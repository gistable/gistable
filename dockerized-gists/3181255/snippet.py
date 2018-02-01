"""
A simple example that generates a random figure and serves it using Bottle
"""

import numpy as np
import StringIO

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from bottle import Bottle, run, response

app = Bottle()


@app.route("/test")
def test():

    fig = Figure()
    ax = fig.add_subplot(111)
    ax.imshow(np.random.rand(100, 100), interpolation='nearest')
    canvas = FigureCanvas(fig)
    png_output = StringIO.StringIO()
    canvas.print_png(png_output)
    response.content_type = 'image/png'
    return png_output.getvalue()

run(app, host='localhost', port=8080)