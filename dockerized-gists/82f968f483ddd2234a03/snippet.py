def cumsum(softmax):
  values = tf.split(1, softmax.get_shape()[1], softmax)
  out = []
  prev = tf.zeros_like(values[0])
  for val in values:
      s = prev + val
      out.append(s)
      prev = s
  cumsum = tf.concat(1, out)
  return cumsum