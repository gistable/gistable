import matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot
import numpy

from flask import Flask, send_file
from cStringIO import StringIO

app = Flask(__name__)


def plot(image):
    x = numpy.linspace(0, 10)
    y = numpy.sin(x)
    pyplot.plot(x, y)
    pyplot.savefig(image, format='png')


@app.route('/image.png')
def image_png():
    image = StringIO()
    plot(image)
    image.seek(0)
    return send_file(image,
                     attachment_filename="image.png",
                     as_attachment=True)


@app.route('/')
def index():
    return '<img src="image.png">'


app.run(debug=True)
