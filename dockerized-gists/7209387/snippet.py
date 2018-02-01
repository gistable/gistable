class NoRequestParamsPredicate(object):
    def __init__(self, val, config):
        self.val = bool(val)

    def text(self):
        return 'no_request_params = %s' % self.val

    phash = text

    def __call__(self, context, request):
        params_do_not_exist = len(request.params) == 0
        return params_do_not_exist is self.val