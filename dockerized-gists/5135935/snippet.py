class directory(object):
    """ pushd/popd context manager.

    Use like:
                                     
        >>> with directory("/tmp/"):
        ...     pass # do some stuff

    """ 
    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self, *args, **kw):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, *args, **kw):
        os.chdir(self.savedPath)
