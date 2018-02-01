# Probability of a segmentation =
#   Probability(first word) * Probability(rest)
# Best segmentation = 
#   one with highest probability
# Probability(word)
#   estimated by counting

# Eg. Best segmentation("nowisthetime...")
# Pf("n") * Pr("owisthetime...") = .003% * 10^-30% = 10^-34%
# Pf("no") * Pr("wisthetime...") = .26% * 10^-26% = 10^-29%
# Pf("now") * Pr("isthetime...") = .23% * 10^-21% = 10^-24%
# Pf("nowi") * Pr("sthetime...") = 10^-7% * 10^-21% = 10^-30%
# ...

from utils import Pw, product, memo

def splits(characters, longest=12):
    "All ways to split chars into a first word and remainder"
    return [(characters[:i], characters[i:])
            for i in range(1, 1+min(longest, len(characters)))]
            
def Pwords(words): return product(words, key=Pw)

@memo
def segment(text):
    "Best segmentation of text into words, by probability."
    return [] if (text =="") else (
        max([[first]+segment(rest) for first, rest in splits(text)],
            key=Pwords))