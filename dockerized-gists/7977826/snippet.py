def group_by(dictionary):
    d = {}
    for k, v in dictionary.iteritems():
        d.setdefault(k, []).append(v)
    return d