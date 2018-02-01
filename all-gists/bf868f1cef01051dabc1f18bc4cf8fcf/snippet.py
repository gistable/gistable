def find_similar_words(embed,text,refs,thresh):

    C = np.zeros((len(refs),embed.W.shape[1]))

    for idx, term in enumerate(refs):
        if term in embed.vocab:
            C[idx,:] = embed.W[embed.vocab[term], :]


    tokens = text.split(' ')
    scores = [0.] * len(tokens)
    found=[]

    for idx, term in enumerate(tokens):
        if term in embed.vocab:
            vec = embed.W[embed.vocab[term], :]
            cosines = np.dot(C,vec.T)
            score = np.mean(cosines)
            scores[idx] = score
            if (score > thresh):
                found.append(term)
    print scores

    return found