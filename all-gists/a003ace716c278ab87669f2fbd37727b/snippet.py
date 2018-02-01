import math
from functools import wraps

from theano import tensor as T
from theano.sandbox.rng_mrg import MRG_RandomStreams as RandomStreams

from lasagne import init
from lasagne.random import get_rng

__all__ = ['Accumulator', 'NormalApproximation', 'NormalApproximationScMix', 'bbpwrap']

c = - 0.5 * math.log(2 * math.pi)


def log_normal(x, mean, std, eps=0.0):
    std += eps
    return c - T.log(T.abs_(std)) - (x - mean) ** 2 / (2 * std ** 2)


def log_normal3(x, mean, rho, eps=0.0):
    std = T.log1p(T.exp(rho))
    return log_normal(x, mean, std, eps)


class Accumulator(object):
    def __init__(self):
        """
        A simple class for accumulating any cost
        Used in layers with BayesianMeta
        """
        self.srng = RandomStreams(get_rng().randint(1, 2147462579))
        self.total = []

    def get_cost(self):
        return sum(map(T.sum,self.total))

    def add_cost(self, new):
        self.total.append(new)


class NormalApproximation(object):
    def __init__(self, pm=0, pstd=T.exp(-3)):
        self.pm = pm
        self.pstd = pstd

    def log_prior(self, x):
        return log_normal(x, self.pm, self.pstd)

    def __call__(self, layer, spec, shape, **tags):
        # case when user uses default init specs
        if not isinstance(spec, dict):
            spec = {'mu': spec}
        # important!
        # we declare that params we add next
        # are the ones we need to fit the distribution
        tags['variational'] = True

        rho_spec = spec.get('rho', init.Normal(1))
        mu_spec = spec.get('mu', init.Normal(1))

        rho = layer.add_param(rho_spec, shape, **tags)
        mean = layer.add_param(mu_spec, shape, **tags)

        e = layer.acc.srng.normal(shape, std=1)
        W = mean + T.log1p(T.exp(rho)) * e

        q_p = self.log_posterior_approx(W, mean, rho) - self.log_prior(W)
        layer.acc.add_cost(q_p)
        return W

    @staticmethod
    def log_posterior_approx(W, mean, rho):
        return log_normal3(W, mean, rho)


class NormalApproximationScMix(NormalApproximation):
    def __init__(self, pm1=.0, pstd1=.5, pi=.5, pm2=.0, pstd2=1e-3):
        """
        :param pi:
            weight for first Gaussian
            pi is in [0, 1]
        :param pm1: float
            prior mean for first Gaussian
        :param std1:
            prior std for first Gaussian
        :param pm2:
            prior mean for second Gaussian
        :param std2:
            prior std for second Gaussian
        """
        assert .0 <= pi <= 1., 'Weight %d not in [0, 1]' % pi
        self.pi = pi
        self.pm1 = pm1
        self.pstd1 = pstd1
        self.pm2 = pm2
        self.pstd2 = pstd2

    def log_prior(self, x):
        return self.pi * log_normal(x, self.pm1, self.pstd1) + \
               (1 - self.pi) * log_normal(x, self.pm2, self.pstd2)


def bbpwrap(approximation=NormalApproximation()):
    def decorator(cls):
        def add_param_wrap(add_param):
            @wraps(add_param)
            def wrapped(self, spec, shape, name=None, **tags):
                # we should take care about some user specification
                # to avoid bbp hook just set tags['variational'] = True
                if not tags.get('trainable', True) or tags.get('variational', False):
                    return add_param(self, spec, shape, name, **tags)
                else:
                    # they don't need to be regularized, strictly
                    tags['regularizable'] = False
                    param = self.approximation(self, spec, shape, **tags)
                    return param
            return wrapped

        def init_wrap(__init__):
            @wraps(__init__)
            def wrapped(self, acc, *args, **kwargs):
                self.acc = acc  # type: Accumulator
                __init__(self, *args, **kwargs)
            return wrapped

        cls.approximation = approximation
        cls.add_param = add_param_wrap(cls.add_param)
        cls.__init__ = init_wrap(cls.__init__)

        return cls
    return decorator

