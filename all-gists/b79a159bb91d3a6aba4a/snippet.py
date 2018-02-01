#/usr/bin/env python

from collections import defaultdict

# Test input from i3 api
windows = [{'name': 'window 1', 'id': 1}, {'name': 'window 1', 'id': 2}, {'name': 'window 2', 'id': 3}]
ws = defaultdict(list)

lookup = {}
for w in windows:
    ws[w.get('name')].append(w.get('id'))

for w, ids in ws.items():
    if len(ids) == 1:
        lookup[w] = ids[0]
    else:
        for index, id_ in enumerate(ids):
            window_name = "{}-{}".format(w, index)
            lookup[window_name] = id_


print lookup