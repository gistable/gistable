"""
This gist demonstrates that spark 1.0.0 and 0.9.1
don't serialize a logger instance properly when code runs on workers.

run this code via:    
   spark-submit spark_serialization_demo.py
    - or -
   pyspark spark_serialization_demo.py
"""
import pyspark
from os.path import abspath
import logging

# initialize logger
log = logging.getLogger('alexTest')
_h = logging.StreamHandler()
_h.setFormatter(logging.Formatter("%(levelname)s  %(msg)s"))
log.addHandler(_h)
log.setLevel(logging.DEBUG)
log.info("module imported and logger initialized")



FUNC = 'passes()'


def myfunc(*ignore_args):
    log.debug('logging a line from: %s' % FUNC)
    return 0


def passes():
    mycode_module = __import__('spark_serialization_demo')
    print(textFile.map(mycode_module.myfunc, preservesPartitioning=True).take(5))


def fails():
    print(textFile.map(myfunc, preservesPartitioning=True).take(5))
    raise Exception("Never reach this point because code fails first due to serialization error")
    

if __name__ == '__main__':
    sc = pyspark.SparkContext("local[10]", 'test')
    textFile = sc.textFile("file://%s" % abspath(__file__), 5)
    print('\n\n---')

    FUNC = 'fails()'
    log.info(
        "This example fails because it serializes a function that"
        "does not initialize the logger when the function is unserialized")
    try:
        fails()
    except Exception as err:
        log.error("See, I failed!  Details: %s" % err)

    print('\n---')

    log.info(
        "This example passes because it serializes a module that initializes"
        " the logger when the module is unserialized")
    passes()
