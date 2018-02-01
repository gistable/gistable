# Jie Bao, 2013-07-16
# baojie@gmail.com
# simple Naive Bayes classifier

import nltk
from nltk.corpus import movie_reviews

import random
import os
import json
import pickle

class NaiveBayesClassifier:

    word_features = None
    classifier    = None

    def __init__(self, classifier_pickled = None):
        if classifier_pickled:
            print "Load trained model from", classifier_pickled
            with open(classifier_pickled, 'rb') as model:
                self.word_features, self.classifier = pickle.load(model)

    def tokenize(self, sentence):
        """
        Tokonize the sentence into words. Remove non-needed words
        """
        return [e.lower() for e in sentence.split() if len(e) >= 2]

    def build_corpus(self, labeled_text):
        """
        The input is a list of documents, each member is a pair like ("this is a sentence", "label")

        A corpus is a list of pairs like (['this', 'sentence'], "label")
        """
        corpus = []
        for (words, label) in labeled_text:
            corpus.append((self.tokenize(words), label))
        random.shuffle(corpus)
        return corpus

    def build_features(self, corpus):
        """
        Features are words appear in a corpus
        """
        assert corpus # corpus must be built before

        all_words = []
        for doc, label in corpus:
            all_words.extend(doc)

        word_distribution = nltk.FreqDist(all_words)
        return word_distribution.keys()

    def extract_features(self, document):
        """
        extract features in a document
        """
        assert self.word_features # features must be built before

        document_words = set(document)
        features = {}
        for word in self.word_features:
            features['contains(%s)' % word] = (word in document_words)
        return features

    def training(self, labeled_text, classifier_pickled = None):
        """train a model and save it as pickle (optional)"""
        
        corpus = self.build_corpus(labeled_text)
        assert corpus

        self.word_features = self.build_features(corpus)
        assert self.word_features

        training_set = nltk.classify.util.apply_features(self.extract_features, corpus)
        #pprint.pprint(training_set)

        self.classifier = nltk.NaiveBayesClassifier.train(training_set)
        if classifier_pickled:
            with open(classifier_pickled, 'wb') as pickle_file:
                pickle.dump([self.word_features, self.classifier], pickle_file)

    def classify(self, sentence):
        guess = self.classifier.classify(self.extract_features(sentence.split()))
        return guess

    def test(self, labeled_text):
        assert self.classifier

        error = []
        count = 0
        for doc, label in labeled_text:
            count += 1
            guess = self.classify(doc)
            
            if guess != label:
                #print "Wrong! " + label + " => " + guess
                error.append(doc)

        #print error
        print "error rate:", float(len(error)) / float(count)


def test_classifier():
    print "Loading documents...."
    all_documents = documents = [(' '.join(movie_reviews.words(fileid)), category) 
        for category in movie_reviews.categories() 
        for fileid in movie_reviews.fileids(category)[:500]]

    random.shuffle(all_documents)
    print "    Number of documents", len(all_documents)
    training_documents  = all_documents[len(all_documents)/2+1:]
    test_documents = all_documents[:len(all_documents)/2]

    a = NaiveBayesClassifier()
    # test pickling learning result and load it in another classifier
    print "Training...."
    a.training(training_documents, "model.pkl")
    print "Testing...."
    a.test(test_documents)

    # test pickle
    print "Testing saved model...."
    b = NaiveBayesClassifier("model.pkl") # create another to test
    b.test(test_documents)

if __name__ == '__main__':
    test_classifier()