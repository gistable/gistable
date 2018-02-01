def format_time(secs):
    return "%d:%02d" % (secs / 60, secs % 60)


def invert(arr):
    """
    Make a dictionary that with the array elements as keys and
    their positions positions as values.

    >>> invert([3, 1, 3, 6])
    {1: [1], 3: [0, 2], 6: [3]}
    """
    map = {}
    for i, a in enumerate(arr):
        map.setdefault(a, []).append(i)
    return map


popcnt_table_8bit = [
    0,1,1,2,1,2,2,3,1,2,2,3,2,3,3,4,1,2,2,3,2,3,3,4,2,3,3,4,3,4,4,5,
    1,2,2,3,2,3,3,4,2,3,3,4,3,4,4,5,2,3,3,4,3,4,4,5,3,4,4,5,4,5,5,6,
    1,2,2,3,2,3,3,4,2,3,3,4,3,4,4,5,2,3,3,4,3,4,4,5,3,4,4,5,4,5,5,6,
    2,3,3,4,3,4,4,5,3,4,4,5,4,5,5,6,3,4,4,5,4,5,5,6,4,5,5,6,5,6,6,7,
    1,2,2,3,2,3,3,4,2,3,3,4,3,4,4,5,2,3,3,4,3,4,4,5,3,4,4,5,4,5,5,6,
    2,3,3,4,3,4,4,5,3,4,4,5,4,5,5,6,3,4,4,5,4,5,5,6,4,5,5,6,5,6,6,7,
    2,3,3,4,3,4,4,5,3,4,4,5,4,5,5,6,3,4,4,5,4,5,5,6,4,5,5,6,5,6,6,7,
    3,4,4,5,4,5,5,6,4,5,5,6,5,6,6,7,4,5,5,6,5,6,6,7,5,6,6,7,6,7,7,8,
]

def popcnt(x):
    """
    Count the number of set bits in the given 32-bit integer.
    """
    return (popcnt_table_8bit[(x >>  0) & 0xFF] +
            popcnt_table_8bit[(x >>  8) & 0xFF] +
            popcnt_table_8bit[(x >> 16) & 0xFF] +
            popcnt_table_8bit[(x >> 24) & 0xFF])


def ber(offset):
    """
    Compare the short snippet against the full track at given offset.
    """
    errors = 0
    count = 0
    for a, b in zip(full[offset:], short):
        errors += popcnt(a ^ b)
        count += 1
    return max(0.0, 1.0 - 2.0 * errors / (32.0 * count))


# load fingerprints
full = eval(open('joy_full.txt').read())[0]
short = eval(open('joy_short.txt').read())[0]

# don't use all 32 bits for the initial matching phase
full_20bit = [x & (1<<20 - 1) for x in full]
short_20bit = [x & (1<<20 - 1) for x in short]

# check which items are contained in both fingerprints
common = set(full_20bit) & set(short_20bit)

# create small inverted indexes
i_full_20bit = invert(full_20bit)
i_short_20bit = invert(short_20bit)

# check at which offsets do the common items occur
offsets = {}
for a in common:
    for i in i_full_20bit[a]:
        for j in i_short_20bit[a]:
            o = i - j
            offsets[o] = offsets.get(o, 0) + 1

# evaluate the fingerprints at the best matching offsets and sort the results by score
matches = []
for count, offset in sorted([(v, k) for k, v in offsets.items()], reverse=True)[:20]:
    matches.append((ber(offset), offset))
matches.sort(reverse=True)

# print out the results
for i, (score, offset) in enumerate(matches):
    if score < 0.5:
        break
    secs = int(offset * 0.1238) # each fingerprint item represents 0.1238 seconds
    print "%d. position %s with score %f" % (i + 1, format_time(secs), score)
