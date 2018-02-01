# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

'''
Visualize what pooling and convolutional neurons learned
  by displaying images that gain highest response.

Motivation:

  It is straightforward to visualize filters in the first convolutional layer, 
    but not in deeper layers. One way to visualize a neuron is too find images
    that the neuron fires most one. Inspired by:

  [1]: "Rich feature hierarchies for accurate object detection and semantic 
       segmentation" by Ross Girshick et al., CVPR, 2014, section 3.1


This file has two functions for visualizing high responses:
  1) visualize_conv - for some channels in a convolutional layer.
  2) visualize_pooling - for some neurons in a pooling layer

Note that for a convolutional filter, the max response is searched across 
  both images and x,y coordinates. At the same time, for a pooling neuron,
  the max response is searched only acrooss images because the coordinates
  of pooling neurons are fixed (while conv. filter is shared across x,y.)

Implementation issues:

  The search for maximum across images is approximate -- only one best image 
    from each batch can be included into the result. This is done for simplicity
    -- please contribute by generalizing to several images per batch.

  I use OpenCV for drawing. If you can change to PIL or whatever, 
    please propose a patch.

Usage:

  0) Get python bindings to OpenCV
  1) Examine function 'visualize_excitations'. It has an example of visualizing
       conv2 and pool2 layers.
  2) Change function inference() in cifar10.py so that it also returns 
       conv2 and pool2 tensors. See line 415 of this file.
  3) Train cifar10 by running cifar10_train.py
  4) Run this file.
'''


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import cv2
import numpy as np
import tensorflow as tf
from bisect import bisect_right
from math import ceil

from tensorflow.models.image.cifar10 import cifar10

FLAGS = tf.app.flags.FLAGS

tf.app.flags.DEFINE_string('eval_data', 'test',
                           """Either 'test' or 'train_eval'.""")
tf.app.flags.DEFINE_string('checkpoint_dir', '/tmp/cifar10_train',
                           """Directory where to read model checkpoints.""")
tf.app.flags.DEFINE_integer('num_examples', 10000,
                            """Number of examples to run.""")
tf.app.flags.DEFINE_string('excitation_layer', 'pool2',
                            """Visualize excitations of this layer.""")



def _prepare_patch (img, response, y, x, dst_height, scale,
                    stride, accum_padding, half_receptive_field):
  '''Scale patch, overlay receptive field, and response
  '''
  COLOR = (256,256,256)
  THICKNESS = 2
  
  # resize image
  img = cv2.resize(img, dsize=(0,0), fx=scale, fy=scale,
                   interpolation=cv2.INTER_NEAREST)

  # overlay response value
  cv2.putText(img, '%0.1f' % response, 
              org=(0,int(dst_height*0.9)),
              fontFace=cv2.FONT_HERSHEY_DUPLEX, 
              fontScale=dst_height*0.008, 
              color=COLOR,
              thickness=THICKNESS)

  # show the receptive field of a channel (if a user cared to pass params)
  if accum_padding is None or half_receptive_field is None or stride is None:
    logging.warning ('support displaying receptive field only with user input')
  else:
    x_min = y * stride + accum_padding - half_receptive_field
    x_max = y * stride + accum_padding + half_receptive_field
    y_min = x * stride + accum_padding - half_receptive_field + 1
    y_max = x * stride + accum_padding + half_receptive_field + 1
    x_min = int(x_min*scale)
    x_max = int(x_max*scale)
    y_min = int(y_min*scale)
    y_max = int(y_max*scale)
    cv2.rectangle(img, (x_min,y_min), (x_max,y_max), 
                  color=COLOR, 
                  thickness=THICKNESS)
  return img



def visualize_conv     (sess, images, layer, channels,
                        half_receptive_field=None,
                        accum_padding=None,
                        stride=None,
                        num_excitations=16,
                        num_images=1024,
                        dst_height=96):
  '''
  TL;DR: display some 'images' that receive the strongest response 
    from user-selected 'channels' of a convolutional 'layer'.

  A 64-channel convolutional layer is consists of 64 filters.
  For each of the channels, the corresponding filter naturally fires diffrently
    on different pixels of different images. We're interested in highest responses.
  For each filter, this function searches for such high responses, plus
    the corresponding images and the coordinates of those responses.
  We collect 'num_excitations' images for each filter and stack them into a row.
    Rows from all filters of interest are stacked vetically into the final map.
    For each image, the response value and the receptive field are visualized.

  Args:
    sess:            tensorflow session
    images:          tensor for source images
    layer:           tensor for a convolutional layer response
    channels:        ids of filters of interest, a numpy array.
                       Example: channels=np.asarray([0,1,2]) will result in 3 rows
                       with responses from 0th, 1st, and 2nd filters.
    half_receptive_field:  integer, half of the receptive field for this layer, [1]
    accum_padding:   integer, accumulated padding w.r.t pixels of the input image.
                       Equals 0 when all previous layers use 'SAME' padding
    stride:          integer, equals to multiplication of strides of all prev. layers.
    num_excitations: number of images to collect for each channel
    num_images:      number of input images to search
    dst_height:      will resize each image to have this height
  Returns:
    excitation_map:   a ready-to-show image, similar to R-CNN paper.

  * Suggestions on how to automatically infer half_receptive_field, accum_padding,
    and stride are welcome.
  '''
  assert isinstance(channels, np.ndarray), 'channels must be a numpy array'
  assert len(channels.shape) == 1, 'need 1D array [num_filters]'

  # now shape is [im_id, Y, X, ch]
  assert   layer.get_shape()[0].value == FLAGS.batch_size
  Y      = layer.get_shape()[1].value
  X      = layer.get_shape()[2].value
  num_ch = layer.get_shape()[3].value
  logging.info ('Y: %d, X: %d, num_ch: %d' % (Y, X, num_ch))

  # to shape [ch, Y, X, im_id], because we'll reduce on Y, X, and im_id
  layer0 = tf.transpose(layer, (3,1,2,0))
  layer1 = tf.reshape(layer0, [num_ch, -1])
  # indices of the highest responses across batch, X, and Y
  responses, best_ids = tf.nn.top_k(layer1, k=1)

  # make three lists of empty lists
  resps = [list([]) for _ in xrange(len(channels))]
  imges = [list([]) for _ in xrange(len(channels))]
  yx    = [list([]) for _ in xrange(len(channels))]

  # Start the queue runners.
  coord = tf.train.Coordinator()
  try:
    threads = []
    for qr in tf.get_collection(tf.GraphKeys.QUEUE_RUNNERS):
      threads.extend(qr.create_threads(sess, coord=coord, daemon=True,
                                       start=True))

    # the same as in cifar10_eval, split evaluation by batches
    num_iter = int(ceil(num_images / FLAGS.batch_size))
    for step in range(num_iter):
      logging.debug ('==========')
      logging.info ('step %d out of %d' % (step, num_iter))

      if coord.should_stop():
        break

      best_ids_vec, images_vec, responses_vec = \
              sess.run([best_ids, images, responses])

      # after this point everything is numpy and opencv

      # collect best responding image from the batch for each filter=channel
      for ch_id, ch in enumerate(channels):
        logging.debug ('----------')
        logging.debug ('ch_id: %d, ch: %s' % (ch_id, ch))

        best_response = responses_vec [ch,0]
        best_id       = best_ids_vec  [ch,0]
        logging.debug ('best_id: %d, Y: %d, X: %d' % (best_id, Y, X))
        # undo reshape -- figure out best indices in Y,X,batch_id coordinates
        best_im = best_id % FLAGS.batch_size
        best_y  = int(best_id / FLAGS.batch_size) / X
        best_x  = int(best_id / FLAGS.batch_size) % X
        # take the image
        best_image = images_vec    [best_im,:,:,:]
        logging.debug ('best_im,best_y,best_x: %d,%d,%d, best_response: %f' % 
                       (best_im, best_y, best_x, best_response))

        # look up the insertion point in the sorted responses lists
        i = bisect_right (resps[ch_id], best_response)
        
        # if the previous response is exactly the same, the image must be same too
        if i > 0 and resps[ch_id][i-1] == best_response:
          logging.debug ('got same response. Skip.')
          continue
        
        # insert both response and image into respective lists
        resps[ch_id].insert(i, best_response)
        imges[ch_id].insert(i, best_image)
        yx[ch_id].insert   (i, (best_y, best_x))

        # pop_front if lists went big and added response is better than current min
        if len(resps[ch_id]) > num_excitations:
          del resps[ch_id][0]
          del imges[ch_id][0]
          del    yx[ch_id][0]

        logging.debug (resps)

  except Exception as e:  # pylint: disable=broad-except
    coord.request_stop(e)

  coord.request_stop()
  coord.join(threads, stop_grace_period_secs=10)


  # scale for resizing images
  src_height = images.get_shape()[1].value
  scale = float(dst_height) / src_height

  for ch_id, _ in enumerate(channels):
    for img_id, img in enumerate(imges[ch_id]):

      imges[ch_id][img_id] = _prepare_patch(
            imges[ch_id][img_id], resps[ch_id][img_id], 
            yx[ch_id][img_id][1], yx[ch_id][img_id][0], 
            dst_height, scale,
            stride, accum_padding, half_receptive_field)

    # concatenate images for this channel
    imges[ch_id]  = np.concatenate(list(imges[ch_id]), axis=1)
  # concatenate stripes of all channels into one map
  excitation_map = np.concatenate(list(imges), axis=0)

  return excitation_map





def visualize_pooling  (sess, images, layer, neurons,
                        half_receptive_field=None,
                        accum_padding=None,
                        stride=None,
	                      num_excitations=16,
                        num_images=1024,
                        dst_height=96):
  '''
  TL;DR: display some 'images' that receive the strongest response 
    from user-selected neurons of a pooling 'layer'.

  A pooling layer is of shape Y x X x Channels.
    Each neuron from that layer is connected to a pixel in the output feature map.
    This function visualizes what a neuron have learned by displying images 
      which receive the strongest responses on that neuron.
    We collect 'num_excitations' images for each neuron and stack them into a row.
      Rows from all neurons of interest are stacked vetically into the final map.
      For each image, the response value and the receptive field are visualized.

  Args:
    sess:            tensorflow session
    images:          tensor for source images
    layer:           tensor for a convolutional layer response
    neurons:         neurons to see best excitations for. 
                      It's probably only a fraction of the layer neurons.
                      Example: neurons=np.asarray([[0,1,2],[58,60,4]])
    half_receptive_field:  integer, half of the receptive field for this layer, [1]
    accum_padding:   integer, accumulated padding w.r.t pixels of the input image.
                       Equals 0 when all previous layers use 'SAME' padding
    stride:          integer, equals to multiplication of strides of all prev. layers.
    num_excitations: number of images to collect for each channel
    num_images:      number of input images to search
    dst_height:      will resize each image to have this height
  Returns:
    excitation_map:   a ready-to-show image, similar to R-CNN paper.

  * Suggestions on how to automatically infer half_receptive_field, accum_padding,
    and stride are welcome.
  '''
  assert isinstance(neurons, np.ndarray), 'neurons must be a numpy array'
  assert len(neurons.shape) == 2 and neurons.shape[1] == 3, 'need shape [N,3]'

  # indices of the "most exciting" patches in a batch, for each neuron
  _, best_ids = tf.nn.top_k(tf.transpose(layer, (1,2,3,0)), k=1)

  # make two lists of empty lists
  # will store num_excitations of best layer/images for each neuron
  resps = [list([]) for _ in xrange(len(neurons))]
  imges = [list([]) for _ in xrange(len(neurons))]

  # Start the queue runners.
  coord = tf.train.Coordinator()
  try:
    threads = []
    for qr in tf.get_collection(tf.GraphKeys.QUEUE_RUNNERS):
      threads.extend(qr.create_threads(sess, coord=coord, daemon=True,
                                       start=True))

    # the same as in cifar10_eval, split evaluation by batches
    num_iter = int(ceil(num_images / FLAGS.batch_size))
    for step in range(num_iter):
      logging.debug ('==========')
      logging.info ('step %d out of %d' % (step, num_iter))

      if coord.should_stop():
        break

      best_ids_mat, images_mat, responses_mat = sess.run(
               [best_ids, images, layer]) 

      # after this point everything is numpy and opencv

      # collect best responding image from the batch for each neuron=[y,x,ch]
      for n_id, n in enumerate(neurons):
        logging.debug ('----------')
        logging.debug ('n_id: %d, n: %s' % (n_id, str(n)))

        best_id       = best_ids_mat  [n[0],n[1],n[2],0]
        best_image    = images_mat    [best_id,:,:,:]
        best_response = responses_mat [best_id,n[0],n[1],n[2]]
        logging.debug ('best_id: %d, best_response: %f' % (best_id, best_response))

        # look up the insertion point in the sorted responses lists
        i = bisect_right (resps[n_id], best_response)
        
        # if the previous response is exactly the same, the image must be same too
        if i > 0 and resps[n_id][i-1] == best_response:
          logging.debug ('got same response. Skip.')
          continue
        
        # insert both response and image into respective lists
        resps[n_id].insert(i, best_response)
        imges[n_id].insert(i, best_image)

        # pop_front if lists went big and added response is better than current min
        if len(resps[n_id]) > num_excitations:
          del resps[n_id][0]
          del imges[n_id][0]

        logging.debug (resps)

  except Exception as e:  # pylint: disable=broad-except
    coord.request_stop(e)

  coord.request_stop()
  coord.join(threads, stop_grace_period_secs=10)


  # scale for resizing images
  src_height = images.get_shape()[1].value
  scale = float(dst_height) / src_height

  for n_id, n in enumerate(neurons):
    for img_id, img in enumerate(imges[n_id]):

      imges[n_id][img_id] = _prepare_patch(
            imges[n_id][img_id], resps[n_id][img_id], 
            n[1], n[0], 
            dst_height, scale,
            stride, accum_padding, half_receptive_field)

    # concatenate images for this neuron, and then all the resultant stripes
    imges[n_id]  = np.concatenate(list(imges[n_id]), axis=1)
  excitation_map = np.concatenate(list(imges), axis=0)

  return excitation_map





def visualize_excitations():
  ''' Restore a trained model, and run one of the visualizations. '''
  with tf.Graph().as_default():
    # Get images for CIFAR-10.
    eval_data = FLAGS.eval_data == 'test'
    images, _ = cifar10.inputs(eval_data=eval_data)

    # Get conv2 and pool2 responses
    _, conv2, pool2 = cifar10.inference(images)

    # Restore the moving average version of the learned variables for eval.
    variable_averages = tf.train.ExponentialMovingAverage(
        cifar10.MOVING_AVERAGE_DECAY)
    variables_to_restore = variable_averages.variables_to_restore()
    saver = tf.train.Saver(variables_to_restore)

    with tf.Session() as sess:
      ckpt = tf.train.get_checkpoint_state(FLAGS.checkpoint_dir)
      if ckpt and ckpt.model_checkpoint_path:
        # Restores from checkpoint
        saver.restore(sess, ckpt.model_checkpoint_path)
      else:
        print('No checkpoint file found')
        return

      if FLAGS.excitation_layer == 'conv2':
        channels=np.asarray([0,31,63])   # first, 31st, and last channels
        excitation_map = visualize_conv     (sess, images, conv2, channels,
                                             half_receptive_field=5,
                                             accum_padding=0,
                                             stride=2,
                                             dst_height=96,
                                             num_images=FLAGS.num_examples)

      elif FLAGS.excitation_layer == 'pool2':
        neurons=np.asarray([[0,0,0],     # top-left corner of first map
                            [5,5,63],    # bottom-right corner of last map
                            [3,4,5]])    # in the middle of 5th map
        excitation_map = visualize_pooling  (sess, images, pool2, neurons,
                                             half_receptive_field=6,
                                             accum_padding=0,
                                             stride=4,
                                             dst_height=96,
                                             num_images=FLAGS.num_examples)

      else:
        raise Exception ('add your own layers and parameters')

      excitation_map = cv2.cvtColor(excitation_map, cv2.COLOR_RGB2BGR)
      cv2.imshow('excitations', excitation_map)
      cv2.waitKey(-1)



def main(argv=None):  # pylint: disable=unused-argument
  logging.basicConfig (level=logging.INFO)

  cifar10.maybe_download_and_extract()
  visualize_excitations()


if __name__ == '__main__':
  tf.app.run()

