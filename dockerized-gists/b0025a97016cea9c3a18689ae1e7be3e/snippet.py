"""

Takes two files produced by fastText's print-word-vectors or print-sentence-vectors and compares the vectors by similarity.

(See https://github.com/facebookresearch/fastText.)

This can be useful for benchmarking output or even generating benchmark data.

For example:

    ./fasttext print-sentence-vectors wiki.en.bin < sentences.a.txt > vectors.a.txt
    ./fasttext print-sentence-vectors wiki.en.bin < sentences.b.txt > vectors.b.txt

    python fasttext_similarity.py vectors.a.txt vectors.b.txt > similarities.txt

The output contains only the number, a float in the range 0 to 1.

"""

import numpy as np

def similarity(v1, v2):
    n1 = np.linalg.norm(v1)
    n2 = np.linalg.norm(v2)
    return np.dot(v1, v2) / n1 / n2

DIM = 300

def vector(line):
    """ Line is in the format output by print-sentence-vector """
    v = line.split()[-DIM:]
    return list(map(float, v))

def similarities(f1, f2, p=False):
    sims = []
    with open(f1) as f1, open(f2) as f2:
        for line1, line2 in zip(f1, f2):
            v1, v2 = vector(line1), vector(line2)
            sim = similarity(v1, v2)
            sims.append(sim)
            if p:
                print(sim)
    return sims

if __name__ == "__main__":
    import sys
    f1 = sys.argv[1]
    f2 = sys.argv[2]
    similarities(f1, f2,  p=True)
