import autograd.numpy as np
import autograd.numpy.random as npr
from autograd import grad, jacobian, hessian, make_vjp
from autograd.core import backward_pass

# explicit dense version, for testing
def make_dense_ggnvp(f, g=lambda x: 1./2*np.dot(x, x)):
  def ggnvp_maker(x):
    J = jacobian(f)(x)
    H = hessian(g)(f(x))
    def ggnvp(v):
      return np.dot(J.T, np.dot(H, np.dot(J, v)))
    return ggnvp
  return ggnvp_maker

# this code runs f forward twice, which we might be able to avoid
def make_ggnvp(f, g=lambda x: 1./2*np.dot(x, x)):
  def grad_h(x):
    f_vjp, _ = make_vjp(f)(getval(x))
    return f_vjp(grad(g)(f(x)))
  def ggnvp_maker(x):
    return make_vjp(grad_h)(x)[0]
  return ggnvp_maker

###

def check_ggnvp(f, x, v):
  gnvp = make_ggnvp(f)(x)
  gnvp2 = make_dense_ggnvp(f)(x)
  return np.allclose(gnvp(v), gnvp2(v))


A = npr.randn(5, 4)
x = npr.randn(4)
v = npr.randn(4)

print check_ggnvp(lambda x: np.dot(A, x), x, v)
print check_ggnvp(lambda x: np.tanh(np.dot(A, x)), x, v)