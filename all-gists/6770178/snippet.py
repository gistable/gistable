#!/usr/bin/env python
'''
Simple test script to see if we get ValueErrors with joblib and the current
version of Python
'''
import logging
import sys
from multiprocessing import cpu_count

import sklearn.datasets
from sklearn.grid_search import GridSearchCV
from sklearn.svm import LinearSVC


# Python 2.x backward compatibility
if sys.version_info < (3, 0):
    range = xrange


def main():
    '''
    Run a simple test
    '''

    # initialize the logger
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    # Load test data
    logging.info('Loading iris data...')
    iris = sklearn.datasets.load_iris()

    # Set number of folds to be twice as many cores as we have
    num_folds = int(cpu_count() * 2.5)

    # Try to grid search a whole bunch of times
    for i in range(1000):
        logging.info('Grid search run {0} out of 1000'.format(i))
        GridSearchCV(LinearSVC(), param_grid={'C': [1, 10]}, n_jobs=num_folds,
                     cv=num_folds).fit(iris.data, iris.target)


if __name__ == '__main__':
    main()
