from werkzeug.routing import NumberConverter, ValidationError

class NegativeFloatConverter(NumberConverter):
    regex = r'\-?\d+\.\d+'
    num_convert = float

    def __init__(self, map, min=None, max=None):
        NumberConverter.__init__(self, map, 0, min, max)

app.url_map.converters['float'] = NegativeFloatConverter