import numpy as np
import matplotlib
import tensorflow as tf
import gzip
import os
import sys
import time


flags = tf.flags
flags.DEFINE_string("output", "train", "whether to output or train")
FLAGS = flags.FLAGS

BATCH_SIZE = 100
IMAGE_SIZE = 30
NUM_CHANNELS = 1
num_images = 1000

def init_weights(shape):
    return tf.Variable(tf.random_normal(shape, stddev=0.01))


def encoder(X, w, w2, wd, wd2):
    b_conv1 = tf.Variable(tf.constant(0.1, shape=[32]))
    l1a = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(X, w,                                 #input 30 x30x1, output 24x24x32
                        strides=[1, 1, 1, 1], padding='VALID'), b_conv1))
    l1 = tf.nn.max_pool(l1a, ksize=[1, 2, 2, 1],                        #input 24x24x32, output 12x12x32
                        strides=[1, 2, 2, 1], padding='SAME')
    
    b_conv2 = tf.Variable(tf.constant(0.1, shape=[64]))
    l2a = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(l1, w2,                               
                        strides=[1, 1, 1, 1], padding='VALID'), b_conv2))          #input 12x12x32, output 8x8x64
    l2 = tf.nn.max_pool(l2a, ksize=[1, 2, 2, 1],                        #input 8x8x64, output 4x4x64
                        strides=[1, 2, 2, 1], padding='SAME')

    #nearest neighbour upsampling                                        
    
    l1da = tf.image.resize_images(l2, 8,                                   #input 4x4x64, output 8x8x64
                        8, 1, align_corners=False)
    # print(l1da.shape)
    b_d_conv1 = tf.Variable(tf.constant(0.1, shape=[32]))
    output_shapel1d = tf.convert_to_tensor([BATCH_SIZE, 12, 12, 32], dtype=tf.int32);
    l1d = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d_transpose(l1da, wd, output_shapel1d,                         #input 8x8x64, output 12x12x32
                        strides=[1, 1, 1, 1], padding='VALID'), b_d_conv1))

    
    #nearest neighbour upsampling                                        
    l2da = tf.image.resize_images(l1d, 24,                                   #input 12x12x32, output 24x24x32
                        24, 1, align_corners=False)

    b_d_conv2 = tf.Variable(tf.constant(0.1, shape=[1]))
    output_shapel2d = tf.convert_to_tensor([BATCH_SIZE, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS], dtype=tf.int32);
    l2d = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d_transpose(l2da, wd2, output_shapel2d,                                 #input 24x24x32, output 30x30x1
                        strides=[1, 1, 1, 1], padding='VALID'), b_d_conv2))
    return l2d


def extract_data(num_start, num_end):
    directory = '/usr/local/lib/python2.7/dist-packages/tensorflow/models/gh_video_prediction/images/images_1k/'
    imagefile_list = []
    for t in range(num_start, num_end):
        imagefile_list.append(directory + 'img_' + `t` + '.jpg')
    filename_queue = tf.train.string_input_producer(imagefile_list)
    image_list = []
    reader = tf.WholeFileReader()
    key,value = reader.read(filename_queue)
    images = tf.image.decode_jpeg(value, channels = 1)
    with tf.Session() as sess:
	    init_op = tf.initialize_all_variables()
	    sess.run(init_op)
	    coord = tf.train.Coordinator()
	    threads = tf.train.start_queue_runners(coord=coord)
	    
	    for i in range(num_start, num_end):
	        image = images.eval() 
	        image_list.append(image)
	    coord.request_stop()
	    coord.join(threads)

    return image_list


def write_data(image_tensor, name_start, name_end):
    print "writing images"
    images_act = []
    directory = '/usr/local/lib/python2.7/dist-packages/tensorflow/models/gh_video_prediction/images/output/'
    with tf.Session() as sess:
        init_op = tf.initialize_all_variables()
        sess.run(init_op)
        count = 0
        for i in range(name_start, name_end):
            #image_tensor = tf.convert_to_tensor(image_list[i], dtype=tf.float32)
            my_img = tf.image.encode_jpeg(image_tensor[count], name="img_"+`i`)
	          count = count + 1
            image = my_img.eval() 
            #images_act.append(image)
            f = open(directory+"img_"+`i`+".jpg", 'wb+')
            f.write(image)
            f.close()

complete_image = extract_data(0, 1000)
trX = complete_image[0:1000]
trY = trX

X = tf.placeholder("float", [BATCH_SIZE, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS])
Y = tf.placeholder("float", [BATCH_SIZE, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS])

w = init_weights([7, 7, 1, 32])       
w2 = init_weights([5, 5, 32, 64])     
wd = init_weights([5, 5, 32, 64])
wd2 = init_weights([7, 7, 1, 32])
py_x = encoder(X, w, w2, wd, wd2)

cost = tf.reduce_mean(tf.squared_difference(py_x, Y, name = None))
train_op = tf.train.RMSPropOptimizer(0.001, 0.9).minimize(cost)
predict_op = py_x;

ckpt_dir = "./ckpt_dir_1k"
if not os.path.exists(ckpt_dir):
    os.makedirs(ckpt_dir)

global_step = tf.Variable(0, name='global_step', trainable=False)

# Call this after declaring all tf.Variables.
saver = tf.train.Saver()

# Launch the graph in a session
with tf.Session() as sess:
    # you need to initialize all variables
    tf.initialize_all_variables().run()

    ckpt = tf.train.get_checkpoint_state(ckpt_dir)
    epoch_cost = 0
    if ckpt and ckpt.model_checkpoint_path:
        print ckpt.model_checkpoint_path
        saver.restore(sess, ckpt.model_checkpoint_path) # restore all variables

    start = global_step.eval() # get last global_step
    print "Start from:", start
    for i in range(start, 1000):
	      epoch_cost = 0
    	  training_batch = zip(range(0, len(trX), BATCH_SIZE),
                           range(BATCH_SIZE, len(trX), BATCH_SIZE))           

        for start, end in training_batch:
            sess.run(train_op, feed_dict={X: trX[start:end], Y: trY[start:end]})
	          batch_cost = sess.run(cost, feed_dict={X: trX[start:end], Y: trY[start:end]})
            epoch_cost += batch_cost
	   
        global_step.assign(i).eval() # set and update(eval) global_step with index, i
        saver.save(sess, ckpt_dir + "/model.ckpt", global_step=global_step)
      	epoch_cost /= 10
        print "cost during epoch " + `i` + "is ", epoch_cost
