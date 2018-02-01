def diff_data(d1, d2, d1_name='d1', d2_name='d2'):
    """Return fields in one but not the other, or None if they're the same.
    """
    if d1 == d2:
        return None
    elif type(d1) != type(d2):
        return {d1_name: d1, d2_name: d2}
    elif isinstance(d1, dict):
        diff = {}
        for key, v1 in d1.iteritems():
            v2 = d2.get(key)
            if v1 != v2:
                diff[key] = diff_data(v1, v2, d1_name, d2_name)
            else:
                diff[key] = v1
        return diff
    elif type(d1) in [str, unicode]:
        return {d1_name: d1, d2_name: d2}
    elif isinstance(d1, list):
        return [v1 != v2 and diff_data(v1, v2, d1_name, d2_name) or v1 \
                for v1, v2 in zip(d1, d2)]

    return {d1_name: d1, d2_name: d2}