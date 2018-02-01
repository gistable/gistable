class with_attrs(object):
    '''
    Decorator to set function attributes
    '''
    def __init__(self, **kwargs):
        self.options = kwargs;

    def __call__(self, f):
        [setattr(f, opt, val) for (opt, val) in self.options.items()]
        return f

