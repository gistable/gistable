import sys

from pyspark.context import SparkContext
from numpy import array, random as np_random
from sklearn import linear_model as lm
from sklearn.base import copy

N = 10000   # Number of data points
D = 10      # Numer of dimensions
ITERATIONS = 5
np_random.seed(seed=42)

def generate_data(N):
    return [[1 if np_random.rand() < 0.5 else 0, np_random.randn(1, D)] for ii in range(N)]

def train(iterator, sgd):
    for x in iterator:
        sgd.partial_fit(x[1], x[0], classes=array([0, 1]))
    yield sgd

def merge(left, right):
    new = copy.deepcopy(left)
    new.coef_ += right.coef_
    new.intercept_ += right.intercept_
    return new

def avg_model(sgd, slices):
    sgd.coef_ /= slices
    sgd.intercept_ /= slices
    return sgd

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print >> sys.stderr, \
            "Usage: PythonLR <master> <iterations> [<slices>]"
        exit(-1)
    #print sys.argv

    sc = SparkContext(sys.argv[1], "PythonLR")
    ITERATIONS = int(sys.argv[2]) if len(sys.argv) > 2 else ITERATIONS
    slices = int(sys.argv[3]) if len(sys.argv) == 4 else 2
    data = generate_data(N)
    print len(data)

    # init stochastic gradient descent
    sgd = lm.SGDClassifier(loss='log')
    # training
    for ii in range(ITERATIONS):
        sgd = sc.parallelize(data, numSlices=slices) \
                .mapPartitions(lambda x: train(x, sgd)) \
                .reduce(lambda x, y: merge(x, y))
        sgd = avg_model(sgd, slices) # averaging weight vector => iterative parameter mixtures
        print "Iteration %d:" % (ii + 1)
        print "Model: "
        print sgd.coef_
        print sgd.intercept_
        print ""