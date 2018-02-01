
docs = [
    [0.5, 0.4, 0.1],
    [0.8, 0.1, 0.1],
    [0.25, 0.25, 0.5]
]

ratings = [1.0/len(docs),] * len(docs)

def normalize(v):
    base = float(sum(v))
    out = map(lambda x: x/base, v)
    assert(abs(sum(out) - 1.0) < 0.001)
    return out

def ratings2interests():
    out = [0.0,] * len(docs[0])
    for tidx in range(len(docs[0])):
        for topics in docs:
            out[tidx] += ratings[tidx] * topics[tidx]
    return normalize(out)

def interests2ratings(interests):
    ratings = []
    for topics in docs:
        tmp = 0.0
        for tidx in range(len(docs[0])):
            tmp += topics[tidx] * interests[tidx]
        ratings.append(tmp)
    return normalize(ratings)

def likelihood(interests):
    L = 0.0
    for score, doc in zip(ratings, docs):
        p = 0.0
        for idx in range(len(doc)):
            p += doc[idx] * interests[idx]
        p *= score
        L += p
    return L

i = 0
last = None
while True:
    i += 1

    print 'ratings', ratings

    # E-step
    interests = ratings2interests()
    print 'interests', interests

    # M-step
    ratings = interests2ratings(interests)

    print '-' * 33

    L = likelihood(interests)
    print 'ITER', i
    print 'Likelihood\t\t', L
    if last != None:
        print 'Delta Likelihood\t', L - last
        if L - last < 1.0e-15:
            print '-' * 33
            print 'THRESHOLD 1.0e-15 MET!!'
            print '-' * 33
            break
    last = L
