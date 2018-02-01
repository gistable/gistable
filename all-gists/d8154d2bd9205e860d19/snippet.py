class SharedPointerPrinter:
    "Print a shared_ptr or weak_ptr"

    def __init__ (self, typename, val):
        self.typename = typename
        self.val = val

    def to_string (self):
        state = 'empty'
        refcounts = self.val['_M_refcount']['_M_pi']
        if refcounts != 0:
            usecount = refcounts['_M_use_count']
            weakcount = refcounts['_M_weak_count']
            if usecount == 0:
                state = 'expired, weak %d' % weakcount
            else:
                state = 'count %d, weak %d' % (usecount, weakcount - 1)
        return '%s (%s) %s' % (self.typename, state, self.val['_M_ptr'])

    def children(self):
        return [(self.val.type.template_argument(0).name, self.val['_M_ptr'][0]), ("state", self.to_string())]


class UniquePointerPrinter:
    "Print a unique_ptr"

    def __init__ (self, typename, val):
        self.val = val
        self.typename = typename

    def to_string (self):
        v = self.val['_M_t']['_M_head_impl']
        return ('std::unique_ptr<%s> containing %s' % (str(v.type.target()),
                                                       str(v)))

    def children(self):
        return [(self.val.type.template_argument(0).name, self.val['_M_t']['_M_head_impl'][0])]
