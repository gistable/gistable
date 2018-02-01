class SqlFileQuery:
    """Utility class to load a named SQL file and use as a query."""
    def __init__(self, filename):
        self.filename = filename
    @property
    def dirpath(self):
        return os.path.dirname(os.path.realpath(__file__))
    @property
    def filepath(self):
        return os.path.join(self.dirpath, self.filename)
    @property
    def query(self):
        with open(self.filepath, mode='r') as f:
            return f.read()
    def __repr__(self):
        return '{}(filename={})'.format(type(self).__name__, repr(self.filename))
    def __str__(self):
        return self.query

