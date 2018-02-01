import math

def fft(data):
  n = len(data)
  assert 2 ** int(math.log(n, 2)) == n, "Number of samples should be 2^n."

  theta = math.pi * 2 / n

  def scramble(k, i):
    while True:
      i ^= k
      if i >= k:
	return i
      k >>= 1

  i = 0
  for j in range(1, n - 1):
    i = scramble(n >> 1, i)
    if j < i:
      (data[i], data[j]) = (data[j], data[i])

  mh = 1
  while True:
    m = mh << 1
    if m > n:
      break

    irev = 0
    for i in range(0, n, m):
      w = math.cos(theta * irev) + math.sin(theta * irev) * 1j
      irev = scramble(n >> 2, irev)
      for j in range(i, i + mh):
	k = j + mh
	(data[j], data[k]) = (data[j] + data[k], (data[j] - data[k]) * w)

    mh = m

def squareWave(n, hz):
  return [float((i * hz) % n) / n > 0.5 and -1 or 1 for i in range(n)]

def sawWave(n, hz):
  return [float((i * hz) % n) / n - 0.5 for i in range(n)]

def sinWave(n, hz):
  return [math.sin(math.pi * 2 * i * hz / n) for i in range(n)]

def dcLevel(n, value):
  return [value] * n

def add(a, b):
  return map(lambda x: x[0] + x[1], zip(a, b))

def mul(a, b):
  return map(lambda x: x[0] * x[1], zip(a, b))

def amp(data, value):
  return [x * value for x in data]

def dump(data, title):
  print '# %s' % title
  i = 0
  for value in data:
    print '%4d %10.6f' % (i, value)
    i += 1

if __name__ == '__main__':
  n = 256

  data = squareWave(n, 60)
  #dump(data, 'input')
  #print

  fft(data)

  dump(map(abs, data), 'result')
