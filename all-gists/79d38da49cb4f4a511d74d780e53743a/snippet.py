"""
  Simple, hacked-up image similarity search using Tensorflow + the inception
  CNN as feature extractor and ANNoy for nearest neighbor search.

  Requires Tensorflow and ANNoy.

  Based on gist code under
    https://gist.github.com/david90/e98e1c41a0ebc580e5a9ce25ff6a972d
"""
from annoy import AnnoyIndex
import os
import sys
import tensorflow as tf
import tensorflow.python.platform
from tensorflow.python.platform import gfile
import numpy as np

def create_graph(model_path):
    """
    create_graph loads the inception model to memory, should be called before
    calling extract_features.

    model_path: path to inception model in protobuf form.
    """
    with gfile.FastGFile(model_path, 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        _ = tf.import_graph_def(graph_def, name='')


def extract_features(image_paths, verbose=False):
    """
    extract_features computed the inception bottleneck feature for a list of images

    image_paths: array of image path
    return: 2-d array in the shape of (len(image_paths), 2048)
    """
    feature_dimension = 2048
    features = np.empty((len(image_paths), feature_dimension))

    with tf.Session() as sess:
        flattened_tensor = sess.graph.get_tensor_by_name('pool_3:0')

        for i, image_path in enumerate(image_paths):
            if verbose:
                print('Processing %s...' % (image_path))

            if not gfile.Exists(image_path):
                tf.logging.fatal('File does not exist %s', image)

            image_data = gfile.FastGFile(image_path, 'rb').read()
            feature = sess.run(flattened_tensor, {
                'DecodeJpeg/contents:0': image_data
            })
            features[i, :] = np.squeeze(feature)

    return features 

if sys.argv[1] == "index":
    print("[!] Creating a new image similarity search index.")
    print("[!] Loading the inception CNN")
    create_graph("./tensorflow_inception_graph.pb")
    print("[!] Done.")
    input_path = sys.argv[2]
    files = os.listdir(input_path)
    images = [ input_path + i for i in files ]
    results = extract_features(images, True)

    print("[!] Done extracting features, building search index")
    ann_index = AnnoyIndex(len(results[0]))
    for i in xrange(len(images)):
        ann_index.add_item(i, results[i])

    print("[!] Constructing trees")
    ann_index.build(80)
    print("[!] Saving the index to '%s'" % sys.argv[3])
    ann_index.save(sys.argv[3])
    print("[!] Saving the filelist to '%s'" % (sys.argv[3] + ".filelist"))
    filelist = file(sys.argv[3] + ".filelist", "wt")
    filelist.write("\n".join(images))
    filelist.close()
elif sys.argv[1] == "search":
    print("[!] Searching for similar images.")
    print("[!] Loading the inception CNN")
    create_graph("./tensorflow_inception_graph.pb")
    print("[!] Done.")
    input_path = sys.argv[2]
    files = os.listdir(input_path)
    images = [ input_path + i for i in files ]
    results = extract_features(images, True)

    ann_index = AnnoyIndex(len(results[0]))
    ann_index.load(sys.argv[3])

    filelist = file(sys.argv[3] + ".filelist", "rt").readlines()
    for i in xrange(len(results)):
        print("[!] Searching for similar images to '%s'" % images[i])
        search_results = ann_index.get_nns_by_vector(results[i], 10,
            include_distances=True)
        for i in xrange(len(search_results[0])):
            print("%f -> %d (%s)" % (search_results[1][i], search_results[0][i],
                filelist[search_results[0][i]][:-1]))

