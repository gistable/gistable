
# coding: utf-8

# # 持续训练
# 
# 问题提出: 如果人脸识别在使用中发现准确率并不够高, 是否可以继续改进? 如何在已有的基础之上继续改进? 
# 
# 解决方法: 建立并联的判别神经网络, 将A人脸的128位编码和待测人脸的128位编码作为输入, 二值判别输出 
# * 路径A: 计算二阶范数距离, 并以原题目中的阈值作为分界, 形成输出
# * 路径B: 待训练神经网络, 早期时参数值都很小, 因此输出值也很小, 但可被训练. 
# 
# 路径A和路径B的加权平均作为最终输出. 

# In[1]:


from keras.models import Sequential
from keras.layers import Conv2D, ZeroPadding2D, Activation, Input, concatenate, Add
from keras.models import Model
from keras.layers.normalization import BatchNormalization
from keras.layers.pooling import MaxPooling2D, AveragePooling2D
from keras.layers.merge import Concatenate
from keras.layers.core import Lambda, Flatten, Dense
from keras.initializers import glorot_uniform, RandomNormal
from keras.engine.topology import Layer
from keras import backend as K
K.set_image_data_format('channels_first')
import cv2
import os
import numpy as np
from numpy import genfromtxt
import pandas as pd
import tensorflow as tf
from fr_utils import *
from inception_blocks_v2 import *

get_ipython().magic('matplotlib inline')
get_ipython().magic('load_ext autoreload')
get_ipython().magic('autoreload 2')

np.set_printoptions(threshold=np.nan)


# In[2]:


FRmodel = faceRecoModel(input_shape=(3, 96, 96))
load_weights_from_FaceNet(FRmodel)


# In[3]:


database = {}
database["danielle"] = img_to_encoding("images/danielle.png", FRmodel)
database["younes"] = img_to_encoding("images/younes.jpg", FRmodel)
database["tian"] = img_to_encoding("images/tian.jpg", FRmodel)
database["andrew"] = img_to_encoding("images/andrew.jpg", FRmodel)
database["kian"] = img_to_encoding("images/kian.jpg", FRmodel)
database["dan"] = img_to_encoding("images/dan.jpg", FRmodel)
database["sebastiano"] = img_to_encoding("images/sebastiano.jpg", FRmodel)
database["bertrand"] = img_to_encoding("images/bertrand.jpg", FRmodel)
database["kevin"] = img_to_encoding("images/kevin.jpg", FRmodel)
database["felix"] = img_to_encoding("images/felix.jpg", FRmodel)
database["benoit"] = img_to_encoding("images/benoit.jpg", FRmodel)
database["arnaud"] = img_to_encoding("images/arnaud.jpg", FRmodel)


# In[ ]:





# # 代数计算路径
# 
# 距离使用norm 2范数进行计算. 输出根据阈值进行sigmoid. 

# In[4]:


test_face=img_to_encoding("images/camera_0.jpg", FRmodel)


# In[11]:


def dist_path(x1,x2,threshold):
    d = tf.norm((x1-x2),axis=-1)
    # output=1-Activation('sigmoid')(d-threshold)
    output = 0.5 - (tf.sign(d-threshold))/2
    return output


# In[12]:


test_face=img_to_encoding("images/camera_0.jpg", FRmodel)
target_face= database["younes"]
d0=np.linalg.norm((test_face-target_face),axis=-1,keepdims=False)[0]
print(d0)
tf.reset_default_graph()

with tf.Session() as test:
    np.random.seed(1)
    faceA_codes = tf.placeholder("float", [1,128])
    faceB_codes = tf.placeholder("float", [1,128])
    A = dist_path(faceA_codes,faceB_codes,0.7)
    test.run(tf.global_variables_initializer())
    
    out = test.run([A], 
                   feed_dict={
                       faceA_codes: test_face, 
                       faceB_codes: target_face, 
                       K.learning_phase(): 0})
    print("out = " + str(out))


# # 修正路径
# 建立一个神经网络引入修正值, 后期可以通过调整修正路径中的参数对结果进行微调. 对于使用范围比较局限的场景, 例如公司员工的人脸识别, 需要泛化的要求较低, 即使修正路径发生了过拟合也可以接受. 
# 
# 为了初期不影响代数路径的结果, 修正路径的参数初始化可以使用均值为0的小量, 使得初始输出结果很小. 

# In[18]:


def tinker_path(x1,x2): 
    X=tf.concat([x1,x2],axis=-1)
#     X = Flatten()(X)
    X = Dense(128, activation='relu', 
              kernel_initializer = RandomNormal(mean=0.0, stddev=0.05, seed=None))(X)
    X = Dense(128, activation='relu', 
              kernel_initializer = RandomNormal(mean=0.0, stddev=0.05, seed=None))(X)
    X = Dense(1, activation='tanh', 
              kernel_initializer = RandomNormal(mean=0.0, stddev=0.05, seed=None))(X)
    return X


# In[19]:


test_face=img_to_encoding("images/camera_0.jpg", FRmodel)
target_face= database["younes"]
d0=np.linalg.norm((test_face-target_face),axis=-1,keepdims=False)[0]
print(d0)
tf.reset_default_graph()

with tf.Session() as test:
    np.random.seed(1)
    faceA_codes = tf.placeholder("float", [1,128])
    faceB_codes = tf.placeholder("float", [1,128])
    A = tinker_path(faceA_codes,faceB_codes)
    test.run(tf.global_variables_initializer())
    
    out = test.run([A], 
                   feed_dict={
                       faceA_codes: test_face, 
                       faceB_codes: target_face, 
                       K.learning_phase(): 0})
    print("out = " + str(out))


# # 合并路径
# 代数计算路径和神经网络路径的结果进行加权平均, 获得最终的结果

# In[20]:


def face_tinker(x1,x2,threshold,alpha):
    paths=[dist_path(x1,x2,threshold), tinker_path(x1,x2)]
    X=Add()([ a*path for (a,path) in zip(alpha,paths)])
    return X


# In[21]:


test_face=img_to_encoding("images/camera_0.jpg", FRmodel)
target_face= database["younes"]

tf.reset_default_graph()

with tf.Session() as test:
    np.random.seed(1)
    faceA_codes = tf.placeholder("float", [1,128])
    faceB_codes = tf.placeholder("float", [1,128])
    threshold = 0.7
    alpha=[0.7,0.3]
    A = face_tinker(faceA_codes,faceB_codes,threshold,alpha)
    test.run(tf.global_variables_initializer())
    
    out = test.run([A], 
                   feed_dict={
                       faceA_codes: test_face, 
#                        faceB_codes: database["felix"], 
                       faceB_codes: target_face, 
                       K.learning_phase(): 0})
    print("out = " + str(out))


# # 修正路径的训练
# todo

# In[ ]:
