class YAML(object):
    """Open a YAML file as a dictionary in a context,
    and update the file when the context is closed.

    Example
    -------
    with YAML('data.yml') as data:
        data['Trial A'] = {'foo': 1, 'bar': 2}
    """
    def __init__(self, filepath):
        self._filepath = filepath
        try:
            data = yaml.load(open(filepath))
        except IOError:
            data = {}
        self._data = data

    def __getitem__(self, key):
        return self._data.__getitem__(self, key)

    def __setitem__(self, key, val):
        self._data.__setitem__(self, key, val)

    def __enter__(self):
        return self._data

    def __exit__(self, type, value, traceback):
        yaml.dump(self._data, open(self._filepath, 'w'),
                  default_flow_style=False)
