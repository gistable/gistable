import numpy as np
import sys, os

# Edit the paths as needed:
caffe_root = '../caffe/'
sys.path.insert(0, caffe_root + 'python')

import caffe

# Path to your combined net prototxt files:
combined_model_root_path = './models/combined_net/'
l_model_root_path = './models/left/2015-07-20/'
r_model_root_path= './models/right/2015-07-20/'

# The pre-trained Caffemodel files:
lnet_file = '_iter_50000.caffemodel'
rnet_file = '_iter_60000.caffemodel'
# Their respective prototxt files:
lnet_proto = 'net.prototxt'
rnet_proto = 'net.prototxt'

# Chdir if your prototxt files specify your training and testing files
# in relative paths:
os.chdir(l_model_root_path)
lnet = caffe.Net(lnet_proto, lnet_file, caffe.TRAIN)

os.chdir(r_model_root_path)
rnet = caffe.Net(rnet_proto, rnet_file, caffe.TRAIN)

os.chdir(combined_model_root_path)
comb_net = caffe.Net('net.prototxt', caffe.TRAIN)

# The layers you want to combine into the new caffe net:
layer_names = ['ff1', 'ff2']

# The two nets we have already loaded:
nets = {
    'l': lnet,
    'r': rnet,
}

# For each of the pretrained net sides, copy the params to
# the corresponding layer of the combined net:
for side, net in nets.items():
    for layer in layer_names:
        W = net.params[layer][0].data[...] # Grab the pretrained weights
        b = net.params[layer][1].data[...] # Grab the pretrained bias
        comb_net.params['{}_{}'.format(side, layer)][0].data[...] = W # Insert into new combined net
        comb_net.params['{}_{}'.format(side, layer)][1].data[...] = b 

# Save the combined model with pretrained weights to a caffemodel file:
comb_net.save('pretrained.caffemodel')