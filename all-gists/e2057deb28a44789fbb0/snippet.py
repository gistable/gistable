#!/usr/bin/env python
# encoding: utf-8

# This file lives in tests/project_test.py in the usual disutils structure
# Remember to set the SPARK_HOME evnironment variable to the path of your spark installation

def add_pyspark_path():
    """
    Add PySpark to the PYTHONPATH
    Thanks go to this project: https://github.com/holdenk/sparklingpandas
    """
    import sys
    import os
    try:
        sys.path.append(os.path.join(os.environ['SPARK_HOME'], "python"))
        sys.path.append(os.path.join(os.environ['SPARK_HOME'],
            "python","lib","py4j-0.8.2.1-src.zip"))
    except KeyError:
        print "SPARK_HOME not set"
        sys.exit(1)

add_pyspark_path() # Now we can import pyspark
from pyspark import SparkContext
from pyspark import SparkConf
import unittest

class GSparkTestCase(unittest.TestCase):
    def setUp(self):
        # Setup a new spark context for each test
        conf = SparkConf()
        conf.set("spark.executor.memory","1g")
        conf.set("spark.cores.max", "1")
        #conf.set("spark.master", "spark://192.168.1.2:7077")
        conf.set("spark.app.name", "nosetest")
        self.sc = SparkContext(conf=conf)

    def tearDown(self):
        self.sc.stop()

# This would go in tests/project_test.py
class BasicSparkTests(GSparkTestCase):
    def test_basic_spark(self):
       dataFile = "tests/data/taHeader.csv" # Read a CSV with one line
       data = self.sc.textFile(dataFile)
       lineCount = data.count()
       self.assertEqual(lineCount, 1) # Assert that the data has only one entry
