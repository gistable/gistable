#!/usr/bin/env python
# -*- coding: utf-8 -*-

# this is a quick implementation of http://arxiv.org/abs/1508.06576
# BUT! This is kind of dirty. Lots of hard coding.　

import numpy as np
import math
from chainer import cuda, Function, FunctionSet, gradient_check, Variable, optimizers
import chainer.functions as Fu
from chainer.functions import caffe
import chainer

import matplotlib.pyplot as plt
from scipy.misc import imread, imresize, imsave

def readimage(filename):
    img = imread(filename)
    img = imresize(img,[224, 224])
    img = np.transpose(img,(2,0,1))
    img = img.reshape((1,3,224,224))
    p_data = np.ascontiguousarray(img,dtype=np.float32)
    p = Variable(cuda.to_gpu(p_data))
    return p

def reshape2(conv1_1):
    k=conv1_1.data.shape[1]
    pixels=conv1_1.data.shape[2]*conv1_1.data.shape[3]
    return chainer.functions.reshape(conv1_1,(k,pixels))

# save the image x
def save_x(img,filename="output.png"):
    img = img.reshape((3,224,224))
    img = np.transpose(img,(1,2,0))
    imsave(filename,img)

def forward(x, p, a):
    conv1_1, conv2_1, conv3_1, conv4_1,conv5_1, = func(inputs={'data': x}, outputs=['conv1_1', 'conv2_1', 'conv3_1', 'conv4_1', 'conv5_1'])
    conv1_1F,conv2_1F, conv3_1F, conv4_1F,conv5_1F, = [ reshape2(x) for x in [conv1_1,conv2_1, conv3_1, conv4_1,conv5_1]]
    conv1_1G,conv2_1G, conv3_1G, conv4_1G,conv5_1G, = [ Fu.matmul(x, x, transa=False, transb=True) for x in [conv1_1F,conv2_1F, conv3_1F, conv4_1F,conv5_1F]]
#
    conv1_1,conv2_1, conv3_1, conv4_1,conv5_1, = func(inputs={'data': p}, outputs=['conv1_1', 'conv2_1', 'conv3_1', 'conv4_1', 'conv5_1'])
    conv1_1P,conv2_1P, conv3_1P, conv4_1P,conv5_1P, = [ reshape2(x) for x in [conv1_1,conv2_1, conv3_1, conv4_1,conv5_1]]
#
    L_content = Fu.mean_squared_error(conv4_1F,conv4_1P)/2
#
    conv1_1,conv2_1, conv3_1, conv4_1,conv5_1, = func(inputs={'data': a}, outputs=['conv1_1', 'conv2_1', 'conv3_1', 'conv4_1', 'conv5_1'])
    conv1_1A0,conv2_1A0, conv3_1A0, conv4_1A0,conv5_1A0, = [ reshape2(x) for x in [conv1_1,conv2_1, conv3_1, conv4_1,conv5_1]]
    conv1_1A,conv2_1A, conv3_1A, conv4_1A,conv5_1A, = [ Fu.matmul(x, x, transa=False, transb=True) for x in [conv1_1A0,conv2_1A0, conv3_1A0, conv4_1A0,conv5_1A0]]
#
    #caution! the deviding number is hard coding!
    #this part is correspnding to equation (4) in the original paper
    #to check the current N and M, run the following
    #[x.data.shape  for x in [conv1_1F,conv2_1F, conv3_1F, conv4_1F,conv5_1F]]
    L_style = (Fu.mean_squared_error(conv1_1G,conv1_1A)/(4*64*64*50176*50176)
    + Fu.mean_squared_error(conv2_1G,conv2_1A)/(4*128**128*12544*12544)
    + Fu.mean_squared_error(conv3_1G,conv3_1A)/(4*256*256*3136*3136)
    + Fu.mean_squared_error(conv4_1G,conv4_1A)/(4*512*512*784*784)\
    )/4 # this is equal weighting of E_l
#
    ratio = 0.001 #alpha/beta 
    loss = ratio*L_content + L_style
    return loss 

#main

cuda.init(3)# is GPU ID!!

p=readimage('satoshi_fb.png')#read a content image
a=readimage('style.png')#read a style image

#download a pretraind caffe model from here: https://gist.github.com/ksimonyan/3785162f95cd2d5fee77#file-readme-md
func = caffe.CaffeFunction('VGG_ILSVRC_19_layers.caffemodel')#it takes some time.
func.to_gpu()

x_data=np.random.randn(1,3,224,224).astype(np.float32)
x = Variable(cuda.to_gpu(x_data))

x = readimage('imge230.png') # if you want to start from a exsiting image

savedir="satoshi_fb_adam"

#optimize x(=image) with adam
#note we use numpy for optimization

alpha=1
beta1=0.9
beta2=0.999
eps=1e-8

v=np.zeros_like(cuda.to_cpu(x.data))
m=np.zeros_like(v)

for epoch in xrange(10000):
    t=0
    loss=forward(x,p,a)
    loss.backward()
    grad_cuda=x.grad.copy()
    grad=cuda.to_cpu(grad_cuda)
    t +=1
    m =  beta1*m + (1-beta1)*grad
    v =  beta2*v + (1-beta2)*(grad*grad)
    m_hat=m/(1-np.power(beta1,t))
    v_hat=v/(1-np.power(beta2, t))
    x.data -= cuda.to_gpu( alpha * m_hat / (np.sqrt(v_hat) + eps) )#back it to cuda
    
    with open(savedir+"/log.txt", "a") as f:
        f.write(str(epoch)+','+str(loss.data)+','+str(np.linalg.norm(grad.data))+'\n')
    savename = savedir+'/imge'+str(epoch)+'.png'
    save_x(cuda.to_cpu(x.data),savename)

# #optimize x(=image) with momment
# momentum= 0.9
# lr=100
# v=np.zeros_like(x.data)
# for epoch in xrange(10000):
#     loss=forward(x,p,a)
#     loss.backward()
#     grad=x.grad.copy()
#     v *= momentum
#     v -= lr * grad
#     x.data += v
    
#     with open(savedir+"/log.txt", "a") as f:
#         f.write(str(epoch+315)+','+str(loss.data)+','+str(np.linalg.norm(x.grad))+'\n')
#     savename = savedir+'/imge'+str(epoch+315)+'.png'
#     save_x(x.data,savename)