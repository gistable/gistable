def my_local(init):
    key = object()
    def getter():
        t = _app_ctx_stack.top
        l = getattr(t, 'my_locals')
        if l is None:
            t.my_locals = l = {}
        if key not in l:
            l[key] = init()
        return l[key]
    return LocalProxy(getter)

db = my_local(get_database)