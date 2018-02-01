def extract(d):
    import inspect
    inspect.getouterframes(inspect.currentframe())[1][0].f_locals.update(d)