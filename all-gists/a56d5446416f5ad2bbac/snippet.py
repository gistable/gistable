import theano
import theano.tensor as T
from theano.sandbox.rng_mrg import MRG_RandomStreams as RandomStreams
from theano.tensor.signal.downsample import max_pool_2d
from theano.tensor.extra_ops import repeat
from theano.sandbox.cuda.dnn import dnn_conv

from time import time
import numpy as np
from matplotlib import pyplot as plt
from scipy.misc import imsave, imread
import itertools

from foxhound.utils.load import lfw
from foxhound.utils.vis import color_grid_vis

from passage.inits import uniform, orthogonal
from passage.utils import shared0s, floatX, iter_data, sharedX, shuffle
from passage.activations import rectify, linear, hard_tanh

def make_paths(n_code, n_paths, n_steps=480):
    """
    create a random path through code space by interpolating between random points
    """
    paths = []
    p_starts = np.random.randn(n_paths, n_code)
    for i in range(n_steps/48):
        p_ends = np.random.randn(n_paths, n_code)
        for weight in np.linspace(0., 1., 48):
            paths.append(p_starts*(1-weight) + p_ends*weight)
        p_starts = np.copy(p_ends)

    paths = np.asarray(paths)
    return paths

def Adam(params, cost, lr=0.0002, b1=0.1, b2=0.001, e=1e-8):
    """
    no bias init correction
    """
    updates = []
    grads = T.grad(cost, params)
    for p, g in zip(params, grads):
        m = theano.shared(p.get_value() * 0.)
        v = theano.shared(p.get_value() * 0.)
        m_t = (b1 * g) + ((1. - b1) * m)
        v_t = (b2 * T.sqr(g)) + ((1. - b2) * v)
        g_t = m_t / (T.sqrt(v_t) + e)
        p_t = p - (lr * g_t)
        updates.append((m, m_t))
        updates.append((v, v_t))
        updates.append((p, p_t))
    return updates

srng = RandomStreams()

trX, _, _, _ = lfw(n_imgs='all', flatten=False, npx=64)

trX = floatX(trX)

def log_prior(mu, log_sigma):
    """
    yaost kl divergence penalty
    """
    return 0.5* T.sum(1 + 2*log_sigma - mu**2 - T.exp(2*log_sigma))

def conv(X, w, b, activation):
    z = dnn_conv(X, w, border_mode=int(np.floor(w.get_value().shape[-1]/2.)))
    if b is not None:
        z += b.dimshuffle('x', 0, 'x', 'x')
    return activation(z)

def conv_and_pool(X, w, b=None, activation=rectify):
    return max_pool_2d(conv(X, w, b, activation=activation), (2, 2))

def deconv(X, w, b=None):
    z = dnn_conv(X, w, direction_hint="*not* 'forward!", border_mode=int(np.floor(w.get_value().shape[-1]/2.)))
    if b is not None:
        z += b.dimshuffle('x', 0, 'x', 'x')
    return z

def depool(X, factor=2):
    """ 
    luke perforated upsample 
    http://www.brml.org/uploads/tx_sibibtex/281.pdf 
    """
    output_shape = [
        X.shape[1],
        X.shape[2]*factor,
        X.shape[3]*factor
    ]
    stride = X.shape[2]
    offset = X.shape[3]
    in_dim = stride * offset
    out_dim = in_dim * factor * factor

    upsamp_matrix = T.zeros((in_dim, out_dim))
    rows = T.arange(in_dim)
    cols = rows*factor + (rows/stride * factor * offset)
    upsamp_matrix = T.set_subtensor(upsamp_matrix[rows, cols], 1.)

    flat = T.reshape(X, (X.shape[0], output_shape[0], X.shape[2] * X.shape[3]))

    up_flat = T.dot(flat, upsamp_matrix)
    upsamp = T.reshape(up_flat, (X.shape[0], output_shape[0], output_shape[1], output_shape[2]))

    return upsamp
    
def deconv_and_depool(X, w, b=None, activation=rectify):
  return activation(deconv(depool(X), w, b))

n_code = 512
n_hidden = 2048
n_batch = 128

print 'generating weights'

we = uniform((64, 3, 5, 5))
w2e = uniform((128, 64, 5, 5))
w3e = uniform((256, 128, 5, 5))
w4e = uniform((256*8*8, n_hidden))
b4e = shared0s(n_hidden)
wmu = uniform((n_hidden, n_code))
bmu = shared0s(n_code)
wsigma = uniform((n_hidden, n_code))
bsigma = shared0s(n_code)

wd = uniform((n_code, n_hidden))
bd = shared0s((n_hidden))
w2d = uniform((n_hidden, 256*8*8))
b2d = shared0s((256*8*8))
w3d = uniform((128, 256, 5, 5))
w4d = uniform((64, 128, 5, 5))
wo = uniform((3, 64, 5, 5))

enc_params = [we, w2e, w3e, w4e, b4e, wmu, bmu, wsigma, bsigma] 
dec_params = [wd, bd, w2d, b2d, w3d, w4d, wo]
params = enc_params + dec_params

def conv_gaussian_enc(X, w, w2, w3, w4, b4, wmu, bmu, wsigma, bsigma):
    h = conv_and_pool(X, w)
    h2 = conv_and_pool(h, w2)
    h3 = conv_and_pool(h2, w3)
    h3 = h3.reshape((h3.shape[0], -1))
    h4 = T.tanh(T.dot(h3, w4) + b4)
    mu = T.dot(h4, wmu) + bmu
    log_sigma = 0.5 * (T.dot(h4, wsigma) + bsigma)
    return mu, log_sigma

def deconv_dec(X, w, b, w2, b2, w3, w4, wo):
    h = rectify(T.dot(X, w) + b)
    h2 = rectify(T.dot(h, w2) + b2)
    h2 = h2.reshape((h2.shape[0], 256, 8, 8))
    h3 = deconv_and_depool(h2, w3)
    h4 = deconv_and_depool(h3, w4)
    y = deconv_and_depool(h4, wo, activation=hard_tanh)
    return y

def model(X, e):
    code_mu, code_log_sigma = conv_gaussian_enc(X, *enc_params)

    Z = code_mu + T.exp(code_log_sigma) * e

    y = deconv_dec(Z, *dec_params)

    return code_mu, code_log_sigma, Z, y

print 'theano code'

X = T.tensor4()
e = T.matrix()
Z_in = T.matrix()

code_mu, code_log_sigma, Z, y = model(X, e)

y_out = deconv_dec(Z_in, *dec_params)

rec_cost = T.sum(T.abs_(X - y))
prior_cost = log_prior(code_mu, code_log_sigma)

cost = rec_cost - prior_cost

print 'getting updates'

updates = Adam(params, cost)

print 'compiling'

_train = theano.function([X, e], cost, updates=updates)
_reconstruct = theano.function([X, e], y)
_x_given_z = theano.function([Z_in], y_out)
_z_given_x = theano.function([X, e], Z)

xs = floatX(np.random.randn(100, n_code))

print 'TRAINING'

x_rec = floatX(shuffle(trX)[:100])

t = time()
n = 0.
for e in range(10000):
    costs = []
    for xmb in iter_data(trX, size=n_batch):
        xmb = floatX(xmb)
        cost = _train(xmb, floatX(np.random.randn(xmb.shape[0], n_code)))
        costs.append(cost)
        n += xmb.shape[0]
    print e, np.mean(costs), n/(time()-t)
    samples = _x_given_z(xs)
    recs = _reconstruct(x_rec, floatX(np.ones((x_rec.shape[0], n_code))))
    img1 = color_grid_vis(x_rec, transform=lambda x:((x+1.)/2.).transpose(1, 2, 0), show=False)
    img2 = color_grid_vis(recs, transform=lambda x:((x+1.)/2.).transpose(1, 2, 0), show=False)
    img3 = color_grid_vis(samples, transform=lambda x:((x+1.)/2.).transpose(1, 2, 0), show=False)
    imsave('lfw_source.png', img1)
    imsave('lfw_linear_rec/%d.png'%e, img2)
    imsave('lfw_samples/%d.png'%e, img3)

    if e % 5 == 0:
        for i in range(9):
            path_samples = _x_given_z(floatX(paths[:, i, :]))
            for j, sample in enumerate(path_samples):
                imsave('paths_%d/%d.png'%(i, j), ((sample+1.)/2.).transpose(1, 2, 0))