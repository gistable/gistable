# Code inspired and developed from: 
# http://streamhacker.com/2010/05/10/text-classification-sentiment-analysis-naive-bayes-classifier/

from __future__ import division
import nltk.classify, nltk.corpus, nltk.classify.util
from pylab import *

filebase = '/home/fn'


# AFINN-111 is the distributed version
filename_afinn = filebase + '/data/AFINN/AFINN-111.txt'
afinn = dict(map(lambda (w, s): (unicode(w, 'utf-8'), int(s)), [ 
            ws.strip().split('\t') for ws in open(filename_afinn) ]))

# Development version of AFINN
filename_afinn_dev = filebase + '/fnielsen/data/Nielsen2009Responsible_emotion.csv'
afinn_dev = dict(map(lambda (w, s): (unicode(w, 'utf-8'), int(s)), [ 
            ws.strip().split('\t') for ws in open(filename_afinn_dev) ]))


def features(wordlist):
    return dict([ (word, True) for word in wordlist ])

# Load data set
moviedataset = []
for group in ['neg', 'pos']:
    fids = nltk.corpus.movie_reviews.fileids(group)
    for fid in fids:
        item = (features(nltk.corpus.movie_reviews.words(fileids=[fid])), group)  
        moviedataset.append(item)


# Train classifier
classifier = nltk.classify.NaiveBayesClassifier.train(moviedataset)
classifier.show_most_informative_features(10)
accuracy = nltk.classify.util.accuracy(classifier, moviedataset)
print("Training set accuracy: %.3f" % (accuracy,))


x = []   # AFINN values
y = []   # Movie review classifier probability
wordlist = afinn.keys()
for word in wordlist:
    x.append( afinn[word] ) 
    y.append( classifier.prob_classify({word: True}).prob('pos') )


# Rank correlation
r,p = scipy.stats.spearmanr(x,y)
# Linear regression
(a,b),c,d,e = scipy.linalg.lstsq(np.bmat([np.mat(x).T, np.ones((len(x),1))]), np.mat(y).T)

# Scatter plot of AFINN/movie review training
plot(x, y, '.')
xlabel('AFINN valence')
ylabel('Movie review classifier probability')
hold(True)
plot([-5, 5], [-5*a+b, +5*a+b], linewidth=4)
text(3, 0.05, "$r_s = %.2f$" % r, fontsize=20)
title('Scatter plot of word valances')
show()
# savefig('scatter.png')

# "Misaligned" words
diff = np.abs(np.asarray(x)/10+0.5-y)
results = sorted(zip(diff, wordlist, x, y), reverse=True)[:150]
for result in results:
    print("<tr><td> %.2f <td> %15s <td> %3d <td> %.2f" % result)


print("Most missing words in AFINN")
mif = map(lambda (w,c): w, classifier.most_informative_features(n=25))
for word in mif:
    if not afinn_dev.has_key(word):
        print(word)
