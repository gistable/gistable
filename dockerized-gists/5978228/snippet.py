import collections

def extract_top_ten(str):
    return collections.Counter(str.split()).most_common(10)