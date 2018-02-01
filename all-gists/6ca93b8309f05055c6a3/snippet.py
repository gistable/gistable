# use the following snippet in your ipython notebook shell
import argparse
import tensorflow as tf

tf.app.flags.FLAGS = tf.python.platform.flags._FlagValues()
tf.app.flags._global_parser = argparse.ArgumentParser()