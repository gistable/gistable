from deepcopy import deepcopy
from classytags.core import TagMeta
from classytags.arguments import ARgument
from classytags.helpers import AsTag

def make_as_tag(original, new_name):
    class NewTag(AsTag, original):
        name = new_name
		
        options = deepcopy(original.options)
        options.breakpoints.append('as')
        options.options['as'] = [Argument('varname', required=False, resolve=False)]
        options.all_argument_names.append('varname')

        def get_value(self, *args, **kwargs):
            return original.__class__.render_tag(self, *args, **kwargs)
    attrs = vars(original)
    attrs['options'] = options
    attrs['name'] = name
    attrs['_decorated_function'].__name__ = name
    return TagMeta(new_name, (AsTag, original), attrs)
