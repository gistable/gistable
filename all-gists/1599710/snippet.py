plugins = {}
def get_input_plugins():
    return plugins['input'].items()

class Plugin(object):
    plugin_class = None

    @classmethod
    def register(cls, name):
        plugins[cls.plugin_class][name] = cls


class InputPlugin(Plugin):
    plugin_class = 'input'

    def process_input(self, something):
        raise NotImplementedError

class ExamplePlugin(InputPlugin):
    def process_input(self, something):
        return str(something)

ExamplePlugin.register('example')