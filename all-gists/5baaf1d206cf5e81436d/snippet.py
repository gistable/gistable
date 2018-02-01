# "Colorizing B/W Movies with Neural Nets", 
# Network/Code Created by Ryan Dahl, hacked by samim.io to work with movies 
# BACKGROUND: http://tinyclouds.org/colorize/
# DEMO: https://www.youtube.com/watch?v=_MJU8VK2PI4
# USAGE:
# 1. Download TensorFlow model from: http://tinyclouds.org/colorize/
# 2. Use FFMPEG or such to extract frames from video.
# 3. Make sure your images are 224x224 pixels dimension. You can use imagemagicks "mogrify", here some useful commands:
# mogrify -resize 224x224 *.jpg
# mogrify -gravity center -background black -extent 224x224 *.jpg
# mogrify -colorspace sRGB -type TrueColor *.jpg
# 4. Create a directory "kidframe" next to this python file, put your extracted video frames inside. 
# 5. Make sure to have a directory called "out" next to it. Inside "out" a second directory analogue to first ("kidframe")-
# 6. Run: python forward.py
# 7. Grab your rendered frames at "out/kidframe/xxx0001.jpg". 
# 8. Recombine frames with FFMPEG, e.g:
# cat *.jpg | ffmpeg -f image2pipe -r 25 -vcodec mjpeg -i - -vcodec libx264 out.mp4

import tensorflow as tf
import skimage.transform
from skimage.io import imsave, imread
import os
from os import listdir, path
from os.path import isfile, join

def get_directory(folder):
    foundfile = []

    for path, subdirs, files in os.walk(folder):
        for name in files:
            found = os.path.join(path, name)
            if name.endswith('.jpg'):
                foundfile.append(found)
        break

    foundfile.sort()
    return foundfile

def load_image(path):
    img = imread(path)
    # crop image from center
    short_edge = min(img.shape[:2])
    yy = int((img.shape[0] - short_edge) / 2)
    xx = int((img.shape[1] - short_edge) / 2)
    crop_img = img[yy : yy + short_edge, xx : xx + short_edge]
    # resize to 224, 224
    img = skimage.transform.resize(crop_img, (224, 224))
    # desaturate image
    return (img[:,:,0] + img[:,:,1] + img[:,:,2]) / 3.0

with open("colorize.tfmodel", mode='rb') as f:
    fileContent = f.read()

    graph_def = tf.GraphDef()
    graph_def.ParseFromString(fileContent)
    grayscale = tf.placeholder("float", [1, 224, 224, 1])
    tf.import_graph_def(graph_def, input_map={ "grayscale": grayscale }, name='')

images = get_directory("kidframes")

for image in images:
    print image
    shark_gray = load_image(image).reshape(1, 224, 224, 1)

    with tf.Session() as sess:
        inferred_rgb = sess.graph.get_tensor_by_name("inferred_rgb:0")
        inferred_batch = sess.run(inferred_rgb, feed_dict={ grayscale: shark_gray })
        filename = "out/"+image
        imsave(filename, inferred_batch[0])
        print "saved " + filename
    #sess.close()