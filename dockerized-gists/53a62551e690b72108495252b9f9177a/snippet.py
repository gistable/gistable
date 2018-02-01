# expensive way to compute factorial of n
def factorial(n):
  def f(x):
    return tf.pow(x, n)
  for i in range(n):
    f = tfe.gradients_function(f)
  return f(1.)
