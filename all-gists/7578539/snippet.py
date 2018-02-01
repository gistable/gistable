from pylab import *
from numpy import *
from numpy.linalg import solve
from scipy.integrate import odeint
from scipy.stats import norm, uniform, beta
from scipy.special import jacobi



a = 0.0
b = 3.0
theta=1.0
sigma=sqrt(theta/(2*(a+b+2)))

tscale = 0.05

invariant_distribution = poly1d( [-1 for x in range(int(a))], True)*poly1d( [1 for x in range(int(b))], True)

def eigenvalue(n):
    return theta*n*(n+a+b+1)/(a+b+2)

gaussian_var = norm()
def dW(dt):
    return norm.rvs() / sqrt(dt)

def random_walk(y0, tmax, dt, times = None):
    dt = dt * tscale
    def rhs(y,t):
        return -theta*(y-(a-b)/(a+b+2)) + sqrt(2*theta*(1-y*y)/(a+b+2))*dW(dt/tscale)
    if (times is None):
        times = arange(0,tmax,dt)
    y = zeros(shape=times.shape, dtype=float)
    y[0] = y0
    for i in range(1,y.shape[0]):
        y[i] = y[i-1] + rhs(y[i-1], times[i])*dt
        if abs(y[i]) > 1:
            y[i] = y[i] / abs(y[i])
    return (times, y)

def beta_prior(s, f):
    return poly1d(ones(shape=(s,)), True)*poly1d(-1*ones(shape=(f,)), True)

def poly_to_jacobi(x):
    """x is a poly1d object"""
    xc = x.coeffs
    N = x.order+1
    matrix = zeros(shape=(N,N), dtype=float)
    for i in range(N):
        matrix[N-i-1:N, i] = jacobi(i,a,b).coeffs
    return solve(matrix, xc)

def jacobi_to_poly(x):
    result = poly1d([0])
    for i in range(x.shape[0]):
        result = result + (jacobi(i,a,b)*invariant_distribution)*x[i]
    return result

def jacobi_to_poly_no_invariant(x):
    result = poly1d([0])
    for i in range(x.shape[0]):
        result = result + jacobi(i,a,b)*x[i]
    return result

def propagate_jacobi(pc, t):
    """Takes jacobi coefficients and propagates them"""
    n = arange(pc.shape[0], dtype=float)
    l = theta*n*(n+a+b+1.0)/(a+b+2.0)*tscale
    return exp(-l*t)*pc

def truncate_unnecessary_jacobi(p):
    p_normalized = p / (abs(p).sum())
    cs = cumsum(abs(p_normalized[::-1]))[::-1]
    return p_normalized[where(abs(cs) > 1e-4)]

def pde_solve(prior, t):
    result = zeros(shape=(t.shape[0], prior.shape[0]), dtype=float)
    result[0,:] = prior
    for i in range(1,t.shape[0]):
        result[i,:] = propagate_jacobi(result[i-1,:], t[i]-t[i-1])
    return result

def transform_to_x(pdf, x):
    result = zeros(shape=(pdf.shape[0], x.shape[0]), dtype=float)
    for i in range(0, pdf.shape[0]):
        p = jacobi_to_poly(pdf[i,:])
        result[i,:] = p(x)
        result[i,:] /= result[i,:].sum()
    return result

tmax = 4
prior = beta_prior(40, 20)
prior_in_jacobi = poly_to_jacobi(prior)

dt = 0.1
times = arange(0,tmax,dt)
x = arange(-1,1,0.01)

rw_dt = 0.01
t, y = random_walk(0.35*2-1, tmax, rw_dt)

solution_as_x = zeros(shape=(times.size, x.size), dtype=float)
solution_as_jacobi = None
empirical_ctr = zeros(shape=(4,), dtype=float)
for i in range(0,4):
    nt = int(1.0/dt)
    prior = prior_in_jacobi
    rnd = uniform(0,1)
    if (i > 0):
        nsamples = 40
        r = rnd.rvs(nsamples)
        ctr = (y[i/rw_dt]+1)/2.0
        print "CTR: " + str(ctr)
        success = (r < ctr).sum()
        print "Empirical: " + str(success / float(nsamples))
        evidence = beta_prior( nsamples - success, success)
        prior = None
        j = truncate_unnecessary_jacobi(solution_as_jacobi[int(1/dt)-1])
        prior = poly_to_jacobi(evidence * jacobi_to_poly_no_invariant(j))
        empirical_ctr[i] = success / float(nsamples)

    solution_as_jacobi = pde_solve(prior, times[i*nt:(i+1)*nt])

    solution_as_x[i*nt:(i+1)*nt] = transform_to_x(solution_as_jacobi, x)


plot(arange(0,4), empirical_ctr, 'go')
plot(t, (y+1)/2.0, 'k')

imshow(solution_as_x.transpose(), origin='lower', extent=[0,tmax,0,1])
xlabel("time")
ylabel("CTR")
title("Bayesian Estimate of CTR")
colorbar()



show()
