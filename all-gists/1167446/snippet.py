class Mock(object):
    def __init__(self, *args):
        pass

    def __getattr__(self, name):
        return Mock

for mod_name in ('pygtk', 'gtk', 'gobject', 'argparse'):
    sys.modules[mod_name] = Mock()
