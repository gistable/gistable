def cbv_decorator(decorator):
    """
    Turns a normal view decorator into a class-based-view decorator.
    
    Usage:
    
    @cbv_decorator(login_required)
    class MyClassBasedView(View):
        pass
    """
    def _decorator(cls):
        cls.dispatch = method_decorator(decorator)(cls.dispatch)
        return cls
    return _decorator