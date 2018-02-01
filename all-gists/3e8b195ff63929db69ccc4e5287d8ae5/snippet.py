# git clone from https://github.com/tkarras/progressive_growing_of_gans
# download the snapshot from their Google drive
# use the following code in the same directory to generate random faces
import os
import sys
import time
import glob
import shutil
import operator
import theano
import lasagne 
import dataset
import network
from theano import tensor as T
import config
import misc
import numpy as np
import scipy.ndimage
_, _, G = misc.load_pkl("network-snapshot-009041.pkl")

class Net: pass

net = Net()
net.G = G

import train

num_example_latents = 10
net.example_latents = train.random_latents(num_example_latents, net.G.input_shape)
net.example_labels = net.example_latents
net.latents_var = T.TensorType('float32', [False] * len(net.example_latents.shape))('latents_var')
net.labels_var  = T.TensorType('float32', [False] * len(net.example_latents.shape)) ('labels_var')

net.images_expr = net.G.eval(net.latents_var, net.labels_var, ignore_unused_inputs=True)
net.images_expr = misc.adjust_dynamic_range(net.images_expr, [-1,1], [0,1])
train.imgapi_compile_gen_fn(net)
images = net.gen_fn(net.example_latents[:1], net.example_labels[:1])
misc.save_image(images[0], "fake2b.png", drange=[0,1])