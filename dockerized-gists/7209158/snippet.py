class ExactRequestParamPredicate(object):
    def __init__(self, val, config):
        val = _as_sorted_tuple(val)
        reqs = []
        for p in val:
            k = p
            v = None
            if '=' in p:
                k, v = p.split('=', 1)
                k, v = k.strip(), v.strip()
            reqs.append((k, v))
        self.val = val
        self.reqs = reqs

    def text(self):
        return 'request_param %s' % ','.join(
            ['%s=%s' % (x,y) if y else x for x, y in self.reqs]
        )

    phash = text

    def __call__(self, context, request):

        # predicate params count and request params count must be the same
        if len(self.reqs) != len(request.params):
            return False

        for k, v in self.reqs:
            actual = request.params.get(k)
            if actual is None:
                return False
            if v is not None and actual != v:
                return False
        return True
