from pelican import signals
from pelican.readers import EXTENSIONS, Reader


class NewReader(Reader):
    enabled = True
    file_extensions = ['yeah']

    def read(self, filename):
        metadata = {'title': 'Oh yeah',
                    'category': 'Foo',
                    'date': '2012-12-01'}

        parsed = {}
        for key, value in metadata.items():
            parsed[key] = self.process_metadata(key, value)

        return "Some content", parsed


def get_generators(generators):
    # define a new generator here if you need to
    return generators


def add_reader(arg):
    EXTENSIONS['yeah'] = NewReader


def register():
    signals.get_generators.connect(get_generators)
    signals.initialized.connect(add_reader)