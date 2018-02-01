from __future__ import division
import autograd.numpy as np
from autograd import make_vjp
from math import factorial

import matplotlib.pyplot as plt

def taylor(f, order):
  def improve_approx(g, k):
    return lambda x, v: make_vjp(g)(x, v)[0](v) + f(x) / factorial(k)
  approx = lambda x, v: f(x) / factorial(order)
  for n in range(order):
    approx = improve_approx(approx, order - n - 1)
  return lambda x: lambda v: approx(x, v)

def f(x): return 1./5 * x**3 + 3 * x**2 - x + 1.


t = np.linspace(-10, 10, 100)
approx = taylor(f, 3)(np.zeros_like(t))

plt.plot(t, f(t), 'b-')
plt.plot(t, approx(t), '--', color='orange')
plt.show()