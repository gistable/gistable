from flask import Blueprint
import converters # module containing the custom converter classes

def add_app_url_map_converter(self, func, name=None):
    """
    Register a custom URL map converters, available application wide.

    :param name: the optional name of the filter, otherwise the function name
                 will be used.
    """
    def register_converter(state):
        state.app.url_map.converters[name or func.__name__] = func

    self.record_once(register_converter)

# monkey-patch the Blueprint object to allow addition of URL map converters
Blueprint.add_app_url_map_converter = add_app_url_map_converter

# create the eyesopen Flask blueprint
bp = Blueprint('myblueprint', __name__)

# register the URL map converters that are required
bp.add_app_url_map_converter(converters.FooConverter, 'foo')
bp.add_app_url_map_converter(converters.BarConverter, 'bar')