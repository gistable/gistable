"""Illustration for various types of namespace scopes in TensorFlow.

> python tf_scopes.py
foo_name_scoped :
	v.name= v:0
	v2.name= foo_name_scoped/v2:0
	a.name= Variable:0
	b.name= Variable_1:0
	result_op.name= foo_name_scoped/Add:0
foo_op_scoped :
	v.name= v_:0
	v2.name= foo_op_scoped/v2:0
	a.name= Variable_2:0
	b.name= Variable_3:0
	result_op.name= foo_op_scoped/Add:0
foo_variable_scoped :
	v.name= foo_variable_scoped/v:0
	v2.name= foo_variable_scoped/v2:0
	a.name= Variable_4:0
	b.name= Variable_5:0
	result_op.name= foo_variable_scoped/Add:0
foo_variable_op_scoped :
	v.name= foo_variable_op_scoped/v:0
	v2.name= foo_variable_op_scoped/v2:0
	a.name= Variable_6:0
	b.name= Variable_7:0
	result_op.name= foo_variable_op_scoped/Add:0
"""
import tensorflow as tf
import traceback

def func_name():
  return traceback.extract_stack(None, 2)[0][2]

def foo_name_scoped(a, b):
  name = func_name()
  print name, ":"
  with tf.name_scope(func_name()) as scope:
    v = tf.get_variable("v", 1)
    v2 = tf.Variable([0], name="v2")
    print "\tv.name=", v.name
    print "\tv2.name=", v2.name
    result_op = tf.add(a, b)
  print "\ta.name=", a.name
  print "\tb.name=", b.name
  print "\tresult_op.name=", result_op.name
  return tf.add(a,b)

def foo_op_scoped(a, b):
  name = func_name()
  print name, ":"
  with tf.op_scope([a,b], func_name()) as scope:
    # Variable 'v' already defined in unnamed variable scope by foo_name_scoped
    v = tf.get_variable("v_", 1)
    v2 = tf.Variable([0], name="v2")
    print "\tv.name=", v.name
    print "\tv2.name=", v2.name
    result_op = tf.add(a, b)
  print "\ta.name=", a.name
  print "\tb.name=", b.name
  print "\tresult_op.name=", result_op.name
  return tf.add(a,b)

def foo_variable_scoped(a, b):
  name = func_name()
  print name, ":"
  with tf.variable_scope(func_name()) as scope:
    v = tf.get_variable("v", 1)
    v2 = tf.Variable([0], name="v2")
    print "\tv.name=", v.name
    print "\tv2.name=", v2.name
    result_op = tf.add(a, b)
  print "\ta.name=", a.name
  print "\tb.name=", b.name
  print "\tresult_op.name=", result_op.name
  return tf.add(a,b)

def foo_variable_op_scoped(a, b):
  name = func_name()
  print name, ":"
  # name is not uniquified
  # default_name is used when name is None and it is uniquified.
  with tf.variable_op_scope([a,b], name=None, default_name=func_name()) as scope:
    v = tf.get_variable("v", 1)
    v2 = tf.Variable([0], name="v2")
    print "\tv.name=", v.name
    print "\tv2.name=", v2.name
    result_op = tf.add(a, b)
  print "\ta.name=", a.name
  print "\tb.name=", b.name
  print "\tresult_op.name=", result_op.name
  return tf.add(a,b)

def main(unused_argv):
  foo_name_scoped(tf.Variable(1), tf.Variable(2))
  foo_op_scoped(tf.Variable(1), tf.Variable(2))
  foo_variable_scoped(tf.Variable(1), tf.Variable(2))
  foo_variable_op_scoped(tf.Variable(1), tf.Variable(2))

if __name__ == '__main__':
  app.run()