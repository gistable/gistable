""" https://en.wikipedia.org/wiki/Golomb_sequence """
def golomb(n):
   d = [1]
   for i in range(0, n - 1):
       next_val = d[len(d) - 1] + 1
       d.append(next_val)
       for j in range(0,  d[next_val - 1] - 1):
           d.append(next_val)
   return d
