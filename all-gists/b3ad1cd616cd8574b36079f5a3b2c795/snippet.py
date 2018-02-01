import collections
counter = collections.Counter()
with open(filename) as f:
    for line in f:
        review = line.strip()
        if review:
            counter[review] += 1
votes = dict(counter)