# testing variable order init

import tensorflow as tf

def initialize_all_variables(sess=None):
  """Initializes all uninitialized variables in correct order. Initializers
  are only run for uninitialized variables, so it's safe to run this multiple
  times.

  Args:
      sess: session to use. Use default session if None.
  """

  from tensorflow.contrib import graph_editor as ge
  def make_initializer(var): 
    def f():
      return tf.assign(var, var.initial_value).op
    return f
  
  def make_noop(): return tf.no_op()

  def make_safe_initializer(var):
    """Returns initializer op that only runs for uninitialized ops."""
    return tf.cond(tf.is_variable_initialized(var), make_noop,
                   make_initializer(var), name="safe_init_"+var.op.name).op

  if not sess:
    sess = tf.get_default_session()
  g = tf.get_default_graph()
      
  safe_initializers = {}
  for v in tf.all_variables():
    safe_initializers[v.op.name] = make_safe_initializer(v)
      
  # initializers access variable vaue through read-only value cached in
  # <varname>/read, so add control dependency to trigger safe_initializer
  # on read access
  for v in tf.all_variables():
    var_name = v.op.name
    var_cache = g.get_operation_by_name(var_name+"/read")
    ge.reroute.add_control_inputs(var_cache, [safe_initializers[var_name]])

  sess.run(tf.group(*safe_initializers.values()))
    
  # remove initializer dependencies to avoid slowing down future variable reads
  for v in tf.all_variables():
    var_name = v.op.name
    var_cache = g.get_operation_by_name(var_name+"/read")
    ge.reroute.remove_control_inputs(var_cache, [safe_initializers[var_name]])



################################################################################
# Tests
################################################################################

def simple_test():
  tf.reset_default_graph()
  a = tf.Variable(1)
  b = tf.Variable(a*2)
  sess = tf.InteractiveSession()
  initialize_all_variables()
  assert sess.run(tf.size(tf.report_uninitialized_variables()))==0

def random_test():
  """Make sure variables don't get reinitialized."""
  
  tf.reset_default_graph()
  a = tf.get_variable("A", shape=())
  b = tf.Variable(a, name="B")
  
  sess = tf.InteractiveSession()
  initialize_all_variables()
  
  c = tf.Variable(a, name="C")
  initialize_all_variables()
  
  assert sess.run(tf.equal(a, b))
  assert sess.run(tf.equal(a, c))
  assert sess.run(tf.equal(b, c))

def complex_test():
  tf.reset_default_graph()
  e = tf.Variable(1., name="e")
  f = tf.Variable(e, name="f")
  d = tf.Variable(f, name="d")
  b = tf.Variable(f, name="b")
  c = tf.Variable(d+e, name="c")
  a = tf.Variable(b+c, name="a")

  sess = tf.InteractiveSession()
  initialize_all_variables(sess)
  assert sess.run(a) == 3.
  
if __name__=='__main__':
  simple_test()
  random_test()
  complex_test()
  print("Tests passed")
