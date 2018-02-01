""" Minimal MapProxy Middleware demonstrating the decorate_img API

To run:
  1. Install MapProxy in a virtual enviroment together with Gunicorn
  2. Create a basic MapProxy config and copy this file into the same directory as mapproxy.yaml
  2. Activate virtual environment
  3. Change to the directory containing this file
  4. Run:
      gunicorn -k eventlet --workers=1 --log-file=- mapproxy_decorate:application

"""

from PIL import ImageColor, ImageDraw, ImageFont
from mapproxy.image import ImageSource
from mapproxy.wsgiapp import make_wsgi_app


def annotate_img(image, service, layers, environ, query_extent, **kw):
    # Get the PIL image and convert to RGBA to ensure we can use black
    # for the text
    img = image.as_image().convert('RGBA')

    text = ['service: %s' % service]
    text.append('layers: %s' % ', '.join(layers))
    text.append('srs: %s' % query_extent[0])

    text.append('bounds:')
    for coord in query_extent[1]:
        text.append('  %s' % coord)

    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    fill = ImageColor.getrgb('black')

    line_y = 10
    for line in text:
        line_w, line_h = font.getsize(line)
        draw.text((10, line_y), line, font=font, fill=fill)
        line_y = line_y + line_h

    # Return a new ImageSource specifying the updated PIL image and
    # the image options from the original ImageSource
    return ImageSource(img, image.image_opts)


class RequestInfoFilter(object):
    """
    Simple MapProxy decorate_img middleware.

    Annotates map images with information about the request.
    """
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Add the callback to the WSGI environment
        environ['mapproxy.decorate_img'] = annotate_img

        return self.app(environ, start_response)


# Make an WSGI application and wrap it in the middleware
application = RequestInfoFilter(make_wsgi_app(r'mapproxy.yaml'))