import sys
sys.path.append('../../facenet/src')

import facenet
import argparse
import os
import importlib
import tensorflow as tf
from tqdm import tqdm
import tensorflow.contrib.slim as slim

import numpy as np

from matio import save_mat
import imghdr

def test_png(filename):
    if imghdr.what(filename) == 'png':
        return True
    else:
        return False

def to_rgb(img):
    if img.shape[2] == 1:
        w, h = img.shape[:2]
        ret = np.empty((w, h, 3), dtype=np.uint8)
        ret[:, :, 0] = ret[:, :, 1] = ret[:, :, 2] = img[:, :, 0]
        return ret
    else:
        return img
def read_file(input_queue, image_size):
    # reader = tf.WholeFileReader()
    # key, value = reader.read(filename_queue)

    filename, label = input_queue
    images = []

    # filenames = tf.Print(filenames, data=[input_queue.size()], message="Number left: ")
    
    #for filename in tf.unstack(filenames):

    file_contents = tf.read_file(filename)

    image = tf.cond(tf.py_func(lambda x: x.lower().endswith('.png'), [filename], tf.bool), \
                    lambda: tf.image.decode_png(file_contents), \
                    lambda: tf.image.decode_jpeg(file_contents))

    image = tf.py_func(to_rgb, [image], tf.uint8)
    image = tf.image.resize_image_with_crop_or_pad(image, image_size, image_size)
    image.set_shape((image_size, image_size, 3))
    image = tf.image.per_image_standardization(image)


    return [image], [label]

def input_pipeline(args, filenames, outnames, batch_size, num_epochs=None):
    filename_queue = tf.train.slice_input_producer( \
            [ filenames, outnames ] ,num_epochs=num_epochs, shuffle=False, capacity=args.capacity)
    
    image_list = [ read_file(filename_queue, args.image_size)
                    for _ in range(args.num_threads)]

    image_batch, label_batch = tf.train.batch_join(image_list, batch_size, \
            capacity=4 * args.num_threads * args.batch_size, enqueue_many=True, \
            allow_smaller_final_batch=True)
    return image_batch, label_batch

def main(args):
    with tf.Graph().as_default():
        with tf.Session() as sess:

            input_filenames = []
            output_filenames = []
            input_dir = os.path.abspath(args.input_dir)
            output_dir = os.path.abspath(args.output_dir)

            for path, subdirs, files in os.walk(input_dir):
                for name in files:
                    if name.lower().endswith('.jpg') or name.lower().endswith('.png')  :
                        filename = os.path.join(path, name)
                        
                        out_folder = path.replace(input_dir, output_dir)

                        if not os.path.isdir(out_folder):
                            os.makedirs(out_folder)
                        
                        outname = filename.replace(input_dir, output_dir) + args.file_ending
                        input_filenames += [filename]
                        output_filenames += [outname]
            
            # load the model
            # print("Loading trained model...\n")
            # facenet.load_model(args.trained_model_dir)



            batch_size_placeholder = tf.placeholder(tf.int32, name='batch_size')

            phase_train_placeholder = tf.placeholder(tf.bool, name='phase_train')
            image_batch, label_batch = input_pipeline(args, input_filenames, output_filenames, batch_size_placeholder, 1)

            network = importlib.import_module(args.model_def)
            batch_norm_params = {
                # Decay for the moving averages
                'decay': 0.995,
                # epsilon to prevent 0s in variance
                'epsilon': 0.001,
                # force in-place updates of mean and variance estimates
                'updates_collections': None,
                # Moving averages ends up in the trainable variables collection
                'variables_collections': [ tf.GraphKeys.TRAINABLE_VARIABLES ],
                # Only update statistics during training mode
                'is_training': phase_train_placeholder
            }
            # Build the inference graph
            prelogits, _ = network.inference(image_batch, 0.8, 
                phase_train=phase_train_placeholder, weight_decay=2e-4)
            bottleneck = slim.fully_connected(prelogits, 128, activation_fn=None, 
                    weights_initializer=tf.truncated_normal_initializer(stddev=0.1), 
                    weights_regularizer=slim.l2_regularizer(2e-4),
                    normalizer_fn=slim.batch_norm,
                    normalizer_params=batch_norm_params,
                    scope='Bottleneck', reuse=False)

            embeddings = tf.nn.l2_normalize(bottleneck, 1, 1e-10, name='embeddings')

            restore_vars = [var for var in tf.trainable_variables() if not var.name.startswith('Logits')]

            saver = tf.train.Saver(restore_vars, max_to_keep=3)


            # Initialize the variables (like the epoch counter).
            sess.run(tf.global_variables_initializer())
            sess.run(tf.local_variables_initializer())

            saver.restore(sess, args.pretrained_model)

            nrof_images = len(input_filenames)
            nrof_batches = len(input_filenames) // args.batch_size + 1

            print ("Total number of images: ", nrof_images)

            emb_array = np.zeros((nrof_images, args.embedding_size))
            coord = tf.train.Coordinator()
            threads = tf.train.start_queue_runners(sess=sess, coord=coord)

            print ("Facenet extracting ... \n")

            f_output_filenames = []
            try:
                for i in tqdm(range(nrof_batches)):
                    start_index = i*args.batch_size
                    end_index = min((i+1)*args.batch_size, nrof_images)

                    # paths_batch = input_filenames[start_index:end_index]
                    # images = facenet.load_data(paths_batch, do_random_crop=False, do_random_flip=False, image_size=args.image_size, do_prewhiten=True)

                    batch_size = end_index - start_index
                    feed_dict = { batch_size_placeholder:batch_size, phase_train_placeholder:False}

                    
                    features_batch, names_batch = sess.run([ embeddings, label_batch] , feed_dict=feed_dict)
                    emb_array[start_index:end_index,:] = features_batch

                    f_output_filenames += names_batch.tolist()
                    # name_batch = sess.run(image_batch, feed_dict=feed_dict)
                    # print ("Output length: ", len(name_batch))
                    # print ("name shape: ", name_batch[0].shape)
            except tf.errors.OutOfRangeError:
                print('Done training -- epoch limit reached')
            finally:
                # When done, ask the threads to stop.
                coord.request_stop()

            # Wait for threads to finish.
            coord.join(threads)
            sess.close()

            print ("Extracting features Done. Saving to files ... \n")

            # for i, name in enumerate(output_filenames):
            #     outname = name.replace(input_dir, output_dir) + args.file_ending
            #     output_filenames[i] = outname

            for i in tqdm(range(len(f_output_filenames))):
                save_mat(f_output_filenames[i], emb_array[i, :])


def parse_argument(argv):
    parser = argparse.ArgumentParser(description=
        'Extract facenet features to MegaFace features file')
    parser.add_argument('input_dir', help='Path to MegaFace Features')
    parser.add_argument('output_dir', help='Path to FaceScrub Features')

    parser.add_argument('pretrained_model', help='Deep model to extract features')
    parser.add_argument('--file_ending',help='Ending appended to original photo files. i.e. 11084833664_0.jpg_LBP_100x100.bin => _LBP_100x100.bin',
                        default='_facenet.bin')
    parser.add_argument('--batch_size', type=int, default=128)
    parser.add_argument('--image_size', type=int, default=160)
    parser.add_argument('--embedding_size', type=int, default=128)
    parser.add_argument('--capacity', type=int, default=10000)
    parser.add_argument('--num_threads', type=int, default=4)
    parser.add_argument('--model_def', type=str,
        help='Model definition. Points to a module containing the definition of the inference graph.',\
        default='models.inception_resnet_v1')

    return parser.parse_args(argv)

if __name__ == '__main__':
    main(parse_argument(sys.argv[1:]))