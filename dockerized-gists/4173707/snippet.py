# -*- coding: utf-8 -*-

import math

def jaccard(v1, v2):
    numerator = sum([c in v2 for c in v1])
    denominator = len(v1) + len(v2) - numerator
    return float(numerator) / denominator if denominator != 0 else 0

def dice(v1, v2):
    numerator = sum([c in v2 for c in v1])
    denominator = len(v1) + len(v2)
    return 2 * float(numerator) / denominator if denominator != 0 else 0

def simpson(v1, v2):
    numerator = sum([c in v2 for c in v1])
    denominator = min(len(v1), len(v2))
    return float(numerator) / denominator if denominator != 0 else 0

def cos(v1, v2):
    numerator = sum([v1[c] * v2[c] for c in v1 if c in v2])
    square = lambda x: x * x
    denominator =  math.sqrt(sum(map(square, v1.values())) * sum(map(square, v2.values())))
    return float(numerator) / denominator if denominator != 0 else 0

def jaccard_weight(v1, v2):
    numerator = 0
    denominator = 0
    
    keys = set(v1.keys())
    keys.update(v2.keys())
    
    for k in keys:
        f1 = v1.get(k, 0)
        f2 = v2.get(k, 0)
        numerator += min(f1, f2)
        denominator += max(f1, f2)
    return float(numerator) / denominator if denominator != 0 else 0

def dice_weight(v1, v2):
    numerator = 0
    denominator = 0
    
    keys = set(v1.keys())
    keys.update(v2.keys())
    
    for k in keys:
        f1 = v1.get(k, 0)
        f2 = v2.get(k, 0)
        numerator += min(f1, f2)
        denominator += f1 + f2
    return 2 * float(numerator) / denominator if denominator != 0 else 0

if __name__ == '__main__':
    v1 = {'帰宅': 1, '風呂': 1, '生': 1, '協': 1, '晩': 1, '家': 1, '食べる': 2, '飽きる': 1, 'する': 1}
    v2 = {'帰宅': 1, '思う': 1, '食べる': 1, 'おかず': 1}
    v3 = {'部屋': 1, '人': 1, '寝る': 2, 'いる': 1, '明らか': 1, '携帯': 1, 'いじる': 1, '原因': 1, '一つ': 1}

    print jaccard(v1, v2)
    print jaccard(v1, v3)