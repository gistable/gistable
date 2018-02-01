#!/public/spark-0.9.1/bin/pyspark

import os
import sys

# Set the path for spark installation
# this is the path where you have built spark using sbt/sbt assembly
os.environ['SPARK_HOME'] = "/public/spark-0.9.1"
# os.environ['SPARK_HOME'] = "/home/jie/d2/spark-0.9.1"
# Append to PYTHONPATH so that pyspark could be found
sys.path.append("/public/spark-0.9.1/python")
# sys.path.append("/home/jie/d2/spark-0.9.1/python")

# Now we are ready to import Spark Modules
try:
    from pyspark import SparkContext
    from pyspark import SparkConf

except ImportError as e:
    print ("Error importing Spark Modules", e)
    sys.exit(1)

import numpy as np

from sklearn.cross_validation import train_test_split, Bootstrap
from sklearn.datasets import make_classification
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier
from sklearn import datasets, svm, pipeline
from sklearn.kernel_approximation import RBFSampler
from sklearn.linear_model import SGDClassifier

if __name__ =='__main__':
    conf=SparkConf()
    conf.setMaster("spark://172.18.109.87:7077")
    # conf.setMaster("local")
    conf.setAppName("spark_svm")
    conf.set("spark.executor.memory", "12g")
    sc = SparkContext(conf=conf)
    X, y = make_classification(n_samples=10000, n_features=30, n_classes=2)
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    samples = sc.parallelize(Bootstrap(y.size))
    feature_map_fourier = RBFSampler(gamma=.2, random_state=1)
    fourier_approx_svm = pipeline.Pipeline([("feature_map", feature_map_fourier),
                                            ("svm", SGDClassifier())])
    fourier_approx_svm.set_params(feature_map__n_components=700)
    results = samples.map(lambda (index, _):
                          fourier_approx_svm.fit(X[index], y[index]).score(X_test, y_test)) \
                          .reduce(lambda x,y: x+y)
    final_results = results/ len(Bootstrap(y.size))
    print(final_results)