%matplotlib inline
from __future__ import division

import numpy as np
import tensorflow as tf
import sys
import os
from matplotlib import pyplot as plt
import urllib2

slim = tf.contrib.slim

os.environ["CUDA_VISIBLE_DEVICES"] = '1'
sys.path.append("/home/dpakhom1/workspace/my_models/slim/")

# A place where you have downloaded a network checkpoint -- look at the previous post
checkpoints_dir = '/home/dpakhom1/checkpoints'

from nets import vgg
from preprocessing import vgg_preprocessing

# Load the mean pixel values and the function
# that performs the subtraction
from preprocessing.vgg_preprocessing import (_mean_image_subtraction,
                                            _R_MEAN, _G_MEAN, _B_MEAN)

image_size = vgg.vgg_16.default_image_size


vgg_checkpoint_path = os.path.join(checkpoints_dir, 'vgg_16.ckpt')


url = ("https://upload.wikimedia.org/wikipedia/commons/d/d9/"
           "First_Student_IC_school_bus_202076.jpg")
    
# Open specified url and load image as a string
image_string = urllib2.urlopen(url).read()

# Decode string into matrix with intensity values
image = tf.image.decode_jpeg(image_string, channels=3)

# Convert image to float32 before subtracting the
# mean pixel value
image_float = tf.to_float(image, name='ToFloat')

# Subtract the mean pixel value from each pixel
mean_centered_image = _mean_image_subtraction(image_float,
                                          [_R_MEAN, _G_MEAN, _B_MEAN])

processed_images = tf.expand_dims(mean_centered_image, 0)

upsample_filter_tensor = tf.constant(upsample_filter_np)

# Define the model that we want to use -- specify to use only two classes at the last layer
with slim.arg_scope(vgg.vgg_arg_scope()):
    logits, end_points = vgg.vgg_16(processed_images,
                           num_classes=2,
                           is_training=False,
                           spatial_squeeze=False,
                           fc_conv_padding='SAME')

downsampled_logits_shape = tf.shape(logits)

upsampled_logits_shape = tf.pack([
                                  downsampled_logits_shape[0],
                                  downsampled_logits_shape[1] * factor,
                                  downsampled_logits_shape[2] * factor,
                                  downsampled_logits_shape[3]
                                 ])


upsampled_logits = tf.nn.conv2d_transpose(logits, upsample_filter_tensor,
                                 output_shape=upsampled_logits_shape,
                                 strides=[1, factor, factor, 1])

pred = tf.argmax(upsampled_logits, dimension=3)

# Now we define a function that will load the weights from oficial VGG into our
# variables when we call it. We exclude the weights from the last layer
# which is responsible for class predictions. We do this because 
# we will have different number of classes to predict and we can't
# use the old ones as an initialization. But for the other weights
# we can use them as initialization.

# We get two sets of variables: one is restored from file and
# another one is randomly initialized. We randomly initialize
# the final fully connected layer because we changes the number
# of classes and want to retrain

weights_restored_from_file = slim.get_variables_to_restore(exclude=['vgg_16/fc8'])

weights_randomly_initialized = slim.get_variables_to_restore(include=['vgg_16/fc8'])

init_fn = slim.assign_from_checkpoint_fn(
   vgg_checkpoint_path,
   weights_restored_from_file)

# Initializer of all variables -- should be run first
init_op = tf.initialize_variables(weights_randomly_initialized)

feature_conv_2_2 = end_points['vgg_16/conv4/conv4_3']

with tf.Session() as sess:
    # Run the init operation.
    sess.run(init_op)
    init_fn(sess)
    
    # We can have a look and make sure that it was actually initialized
    # because it [0, 0] there therefore we didn't read them, we restored them
    input_img, first_pred, features = sess.run([image, upsampled_logits, feature_conv_2_2])


import skimage.io as io

temp = features.squeeze()[:, :, 100]

io.imshow(temp)