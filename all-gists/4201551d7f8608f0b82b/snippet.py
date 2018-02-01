import sys
import logging
import numpy
import gensim


logging.basicConfig(level=logging.INFO)

train_sentences = gensim.models.doc2vec.LabeledLineSentence(sys.argv[1])
model = gensim.models.Doc2Vec(train_sentences, size=400, window=8, min_count=2,
                              workers=8)

test_sentences = gensim.models.doc2vec.LabeledLineSentence(sys.argv[2])


# new labels to self.vocab
def add_new_labels(sentences, model):
    sentence_no = -1
    total_words = 0
    vocab = model.vocab
    model_sentence_n = len([l for l in vocab if l.startswith("SENT")])
    n_sentences = 0
    for sentence_no, sentence in enumerate(sentences):
        sentence_length = len(sentence.words)
        for label in sentence.labels:
            label_e = label.split("_")
            label_n = int(label_e[1]) + model_sentence_n
            label = "{0}_{1}".format(label_e[0], label_n)
            total_words += 1
            if label in vocab:
                vocab[label].count += sentence_length
            else:
                vocab[label] = gensim.models.word2vec.Vocab(
                    count=sentence_length)
                vocab[label].index = len(model.vocab) - 1
                vocab[label].code = [0]
                vocab[label].sample_probability = 1.
                model.index2word.append(label)
                n_sentences += 1
    return n_sentences

n_sentences = add_new_labels(test_sentences, model)

# add new rows to model.syn0
n = model.syn0.shape[0]
model.syn0 = numpy.vstack((
    model.syn0,
    numpy.empty((n_sentences, model.layer1_size), dtype=numpy.float32)
))

for i in xrange(n, n + n_sentences):
    numpy.random.seed(
        numpy.uint32(model.hashfxn(model.index2word[i] + str(model.seed))))
    a = (numpy.random.rand(model.layer1_size) - 0.5) / model.layer1_size
    model.syn0[i] = a

# Set model.train_words to False and model.train_labels to True
model.train_words = False
model.train_lbls = True

# train
model.train(test_sentences)

# slice the results
#print model.most_similar(["SENT_1800000"])
model.save(sys.argv[3])