def ascii_deletion_distance(str1, str2):
    from collections import defaultdict
    histogram = defaultdict(int)
    for ch in str1:
        histogram[ch] += 1
    for ch in str2:
        histogram[ch] += 1
    union = set(str1) | set(str2)
    intersection = set(str1) & set(str2)
    result = union - intersection
    # values = [ord(ch) for ch in result]
    out = 0
    for ch in result:
        out += (histogram[ch] * ord(ch))
    return out
