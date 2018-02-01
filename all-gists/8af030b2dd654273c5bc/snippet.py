import sys
sys.path.append('..')

import os
import json
from time import time
import numpy as np
from tqdm import tqdm
from matplotlib import pyplot as plt
from sklearn.externals import joblib

import theano
import theano.tensor as T
from theano.sandbox.cuda.dnn import dnn_conv

from lib import activations
from lib import updates
from lib import inits
from lib.vis import color_grid_vis
from lib.rng import py_rng, np_rng
from lib.ops import batchnorm, conv_cond_concat, deconv, dropout, l2normalize
from lib.metrics import nnc_score, nnd_score
from lib.theano_utils import floatX, sharedX
from lib.data_utils import OneHot, shuffle, iter_data, center_crop, patch
from lib.cv2_utils import min_resize

from load import imagenet

def transform(X):
    X = [min_resize(x, npx) for x in X]
    X = [center_crop(x, npx) for x in X]
    return floatX(X).transpose(0, 3, 1, 2)/127.5 - 1.

def inverse_transform(X):
    X = (X.reshape(-1, nc, npx, npx).transpose(0, 2, 3, 1)+1.)/2.
    return X

nvis = 400
b1 = 0.5
nc = 3
ny = 10
nbatch = 128
npx = 32
nz = 256
ndf = 128
ngf = 128
nx = nc*npx*npx
niter = 30
niter_decay = 30
lr = 0.0002
# ntrain = 100000
ntrain = 1281167

tr_data, te_data, tr_stream, val_stream, te_stream = imagenet(ntrain=ntrain)

te_handle = te_data.open()
vaX, vaY = te_data.get_data(te_handle, slice(0, 10000))
vaX = transform(vaX)

desc = 'imagenet_gan_pretrain_128f_relu_lrelu_7l_3x3_256z'
model_dir = 'models/%s'%desc
samples_dir = 'samples/%s'%desc
if not os.path.exists(model_dir):
    os.makedirs(model_dir)
if not os.path.exists(samples_dir):
    os.makedirs(samples_dir)

relu = activations.Rectify()
sigmoid = activations.Sigmoid()
lrelu = activations.LeakyRectify()
tanh = activations.Tanh()
bce = T.nnet.binary_crossentropy

gifn = inits.Normal(scale=0.02)
difn = inits.Normal(scale=0.02)
gain_ifn = inits.Normal(loc=1., scale=0.02)
bias_ifn = inits.Constant(c=0.)

gw  = gifn((nz, ngf*4*4*4), 'gw')
gg = gain_ifn((ngf*4*4*4), 'gg')
gb = bias_ifn((ngf*4*4*4), 'gb')
gw2 = gifn((ngf*4, ngf*4, 3, 3), 'gw2')
gg2 = gain_ifn((ngf*4), 'gg2')
gb2 = bias_ifn((ngf*4), 'gb2')
gw3 = gifn((ngf*4, ngf*2, 3, 3), 'gw3')
gg3 = gain_ifn((ngf*2), 'gg3')
gb3 = bias_ifn((ngf*2), 'gb3')
gw4 = gifn((ngf*2, ngf*2, 3, 3), 'gw4')
gg4 = gain_ifn((ngf*2), 'gg4')
gb4 = bias_ifn((ngf*2), 'gb4')
gw5 = gifn((ngf*2, ngf, 3, 3), 'gw5')
gg5 = gain_ifn((ngf), 'gg5')
gb5 = bias_ifn((ngf), 'gb5')
gw6 = gifn((ngf, ngf, 3, 3), 'gwx')
gg6 = gain_ifn((ngf), 'gg6')
gb6 = bias_ifn((ngf), 'gb6')
gwx = gifn((ngf, nc, 3, 3), 'gwx')

dw  = difn((ndf, nc, 3, 3), 'dw')
dw2 = difn((ndf, ndf, 3, 3), 'dw2')
dg2 = gain_ifn((ndf), 'dg2')
db2 = bias_ifn((ndf), 'db2')
dw3 = difn((ndf*2, ndf, 3, 3), 'dw3')
dg3 = gain_ifn((ndf*2), 'dg3')
db3 = bias_ifn((ndf*2), 'db3')
dw4 = difn((ndf*2, ndf*2, 3, 3), 'dw4')
dg4 = gain_ifn((ndf*2), 'dg4')
db4 = bias_ifn((ndf*2), 'db4')
dw5 = difn((ndf*4, ndf*2, 3, 3), 'dw5')
dg5 = gain_ifn((ndf*4), 'dg5')
db5 = bias_ifn((ndf*4), 'db5')
dw6 = difn((ndf*4, ndf*4, 3, 3), 'dw6')
dg6 = gain_ifn((ndf*4), 'dg6')
db6 = bias_ifn((ndf*4), 'db6')
dwy = difn((ndf*4*4*4, 1), 'dwy')

gen_params = [gw, gg, gb, gw2, gg2, gb2, gw3, gg3, gb3, gw4, gg4, gb4, gw5, gg5, gb5, gw6, gg6, gb6, gwx]
discrim_params = [dw, dw2, dg2, db2, dw3, dg3, db3, dw4, dg4, db4, dw5, dg5, db5, dw6, dg6, db6, dwy]

def gen(Z, w, g, b, w2, g2, b2, w3, g3, b3, w4, g4, b4, w5, g5, b5, w6, g6, b6, wx):
    h = relu(batchnorm(T.dot(Z, w), g=g, b=b))
    h = h.reshape((h.shape[0], ngf*4, 4, 4))
    h2 = relu(batchnorm(deconv(h, w2, subsample=(2, 2), border_mode=(1, 1)), g=g2, b=b2))
    h3 = relu(batchnorm(deconv(h2, w3, subsample=(1, 1), border_mode=(1, 1)), g=g3, b=b3))
    h4 = relu(batchnorm(deconv(h3, w4, subsample=(2, 2), border_mode=(1, 1)), g=g4, b=b4))
    h5 = relu(batchnorm(deconv(h4, w5, subsample=(1, 1), border_mode=(1, 1)), g=g5, b=b5))
    h6 = relu(batchnorm(deconv(h5, w6, subsample=(2, 2), border_mode=(1, 1)), g=g6, b=b6))
    x = tanh(deconv(h6, wx, subsample=(1, 1), border_mode=(1, 1)))
    return x

def discrim(X, w, w2, g2, b2, w3, g3, b3, w4, g4, b4, w5, g5, b5, w6, g6, b6, wy):
    h = lrelu(dnn_conv(X, w, subsample=(1, 1), border_mode=(1, 1)))
    h2 = lrelu(batchnorm(dnn_conv(h, w2, subsample=(2, 2), border_mode=(1, 1)), g=g2, b=b2))
    h3 = lrelu(batchnorm(dnn_conv(h2, w3, subsample=(1, 1), border_mode=(1, 1)), g=g3, b=b3))
    h4 = lrelu(batchnorm(dnn_conv(h3, w4, subsample=(2, 2), border_mode=(1, 1)), g=g4, b=b4))
    h5 = lrelu(batchnorm(dnn_conv(h4, w5, subsample=(1, 1), border_mode=(1, 1)), g=g5, b=b5))
    h6 = lrelu(batchnorm(dnn_conv(h5, w6, subsample=(2, 2), border_mode=(1, 1)), g=g6, b=b6))
    h6 = T.flatten(h6, 2)
    y = sigmoid(T.dot(h6, wy))
    return y

X = T.tensor4()
Z = T.matrix()

gX = gen(Z, *gen_params)

p_real = discrim(X, *discrim_params)
p_gen = discrim(gX, *discrim_params)

d_cost_real = bce(p_real, T.ones(p_real.shape)).mean()
d_cost_gen = bce(p_gen, T.zeros(p_gen.shape)).mean()
g_cost_d = bce(p_gen, T.ones(p_gen.shape)).mean()

d_cost = d_cost_real + d_cost_gen
g_cost = g_cost_d

cost = [g_cost, d_cost, g_cost_d, d_cost_real, d_cost_gen]

lrt = sharedX(lr)
d_updater = updates.Adam(lr=lrt, b1=b1)
g_updater = updates.Adam(lr=lrt, b1=b1)
d_updates = d_updater(discrim_params, d_cost)
g_updates = g_updater(gen_params, g_cost)
updates = d_updates + g_updates

print 'COMPILING'
t = time()
_train_g = theano.function([X, Z], cost, updates=g_updates)
_train_d = theano.function([X, Z], cost, updates=d_updates)
_gen = theano.function([Z], gX)
print '%.2f seconds to compile theano functions'%(time()-t)

vis_idxs = py_rng.sample(np.arange(len(vaX)), nvis)
vaX_vis = inverse_transform(vaX[vis_idxs])
color_grid_vis(vaX_vis, (20, 20), 'samples/%s_etl_test.png'%desc)

sample_zmb = floatX(np_rng.uniform(-1., 1., size=(nvis, nz)))

def gen_samples(n, nbatch=128):
    samples = []
    n_gen = 0
    for i in range(n/nbatch):
        zmb = floatX(np_rng.uniform(-1., 1., size=(nbatch, nz)))
        xmb = _gen(zmb)
        samples.append(xmb)
        n_gen += len(xmb)
    n_left = n-n_gen
    zmb = floatX(np_rng.uniform(-1., 1., size=(n_left, nz)))
    xmb = _gen(zmb)
    samples.append(xmb)
    return np.concatenate(samples, axis=0)

f_log = open('logs/%s.ndjson'%desc, 'wb')
log_fields = [
    'n_epochs',
    'n_updates',
    'n_examples',
    'n_seconds',
    '1k_va_nnd',
    '10k_va_nnd',
    '100k_va_nnd',
    'g_cost',
    'd_cost',
]

vaX = vaX.reshape(len(vaX), -1)

print desc.upper()
k = 1
n_updates = 0
n_check = 0
n_epochs = 0
n_updates = 0
n_examples = 0
t = time()
for epoch in range(1, niter+niter_decay+1):
    for imb, ymb in tqdm(tr_stream.get_epoch_iterator(), total=ntrain/nbatch):
        imb = transform(imb)
        zmb = floatX(np_rng.uniform(-1., 1., size=(len(imb), nz)))
        if n_updates % (k+1) == 0:
            cost = _train_g(imb, zmb)
        else:
            cost = _train_d(imb, zmb)
        n_updates += 1
        n_examples += len(imb)
    if (epoch-1) % 5 == 0:
        g_cost = float(cost[0])
        d_cost = float(cost[1])
        gX = gen_samples(100000)
        gX = gX.reshape(len(gX), -1)
        va_nnd_1k = nnd_score(gX[:1000], vaX, metric='euclidean')
        va_nnd_10k = nnd_score(gX[:10000], vaX, metric='euclidean')
        va_nnd_100k = nnd_score(gX[:100000], vaX, metric='euclidean')
        log = [n_epochs, n_updates, n_examples, time()-t, va_nnd_1k, va_nnd_10k, va_nnd_100k, g_cost, d_cost]
        print '%.0f %.2f %.2f %.2f %.4f %.4f'%(epoch, va_nnd_1k, va_nnd_10k, va_nnd_100k, g_cost, d_cost)
        f_log.write(json.dumps(dict(zip(log_fields, log)))+'\n')
        f_log.flush()

    samples = np.asarray(_gen(sample_zmb))
    color_grid_vis(inverse_transform(samples), (20, 20), 'samples/%s/%d.png'%(desc, n_epochs))
    n_epochs += 1
    if n_epochs > niter:
        lrt.set_value(floatX(lrt.get_value() - lr/niter_decay))
    if n_epochs in [1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100]:
        joblib.dump([p.get_value() for p in gen_params], 'models/%s/%d_gen_params.jl'%(desc, n_epochs))
        joblib.dump([p.get_value() for p in discrim_params], 'models/%s/%d_discrim_params.jl'%(desc, n_epochs))
