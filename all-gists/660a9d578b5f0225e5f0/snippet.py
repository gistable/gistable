# DreamImage.py - parameterized deepdream with support for multiple models,
# auto-image-scaling, guided dreaming and kaleido mode (self-guided).
# Jim Bumgardner 7-12-15

# this assumes the deploy file is called 'deploy.prototxt' - you may need
# to rename it if using a different model such as googlenet_places205.

# sample invocations that produce nice results:
# python dreamImage.py -i $1.jpg -model ../../caffe/models/googlenet_places205 -end inception_3a/output -iter 20 -octaves 5 -o $1_m3a.jpg
# python dreamImage.py -i $1.jpg -model ../../caffe/models/googlenet_places205 -end inception_3b/output -iter 20 -octaves 5 -o $1_m3b.jpg
# python dreamImage.py -i $1.jpg -model ../../caffe/models/googlenet_places205 -end inception_4a/output -iter 30 -octaves 6 -o $1_m4a.jpg
# python dreamImage.py -i $1.jpg -model ../../caffe/models/bvlc_googlenet -end inception_3b/output -iter 20 -octaves 5 -o $1_g3b.jpg
# python dreamImage.py -i $1.jpg -model ../../caffe/models/bvlc_googlenet -end inception_3a/output -iter 20 -octaves 5 -o $1_g3a.jpg
# python dreamImage.py -i $1.jpg -model ../../caffe/models/bvlc_googlenet -end inception_4a/output -iter 20 -octaves 6 -o $1_g4a.jpg


import os.path, os, time, sys
os.environ['GLOG_minloglevel'] = '3'

from cStringIO import StringIO
import numpy as np
import scipy.ndimage as nd
import PIL.Image
from google.protobuf import text_format
import argparse
import caffe

parser = argparse.ArgumentParser(description='DreamImage - process a single frame')
parser.add_argument('-i',default='clouds_512.jpg', help='input image')
parser.add_argument('-o',default='untitled.jpg', help='output image name')
parser.add_argument('-model',default='../../caffe/models/bvlc_googlenet', help='caffe model path')
parser.add_argument('-deploy',default='', help='caffe model deploy file override')
parser.add_argument('-end',default='inception_3b/output', help='caffe end layer')
parser.add_argument('-iter',  default=10, type=int, help='Iterations, def=10')
parser.add_argument('-octaves',  default=4, type=int, help='Octaves, def=4')
parser.add_argument('-oscale',  default=1.4, type=float, help='Octave scale, def=1.4')
parser.add_argument('-debug',  default=0, type=int, help='Debugging level')
parser.add_argument('-keys',  default=False, action='store_true', help='Output keys')
parser.add_argument('-gpu',  default=False, action='store_true', help='Use gpu')
parser.add_argument('-force',  default=False, action='store_true', help='Force file overwrite')
parser.add_argument('-kaleido',  default=False, action='store_true', help='Kaleido mode - uses source image as guide')
parser.add_argument('-guide',  default='', help='Guide image')
parser.add_argument('-raw',  default=False, action='store_true', help='Don\'t rescale image')

args = parser.parse_args()

st = time.time()

imgName = args.i
if not os.path.exists(imgName):
    if 'jpg' in imgName and os.path.exists(imgName[:len(imgName)-4]+'.png'):
        imgName = imgName[:len(imgName)-4]+'.png'
    else:
        print "Can't find image"
        sys.exit()

outName = args.o
if os.path.isfile(outName) and not args.force:
    print "File exists"
    sys.exit()

model_path = args.model # '../../caffe/models/bvlc_googlenet/' # substitute your path here
if model_path[-1] == '/':
    model_path = model_path[:-1]
if args.deploy == '':
    net_fn   = model_path + '/deploy.prototxt'
else:
    net_fn   = args.deploy
param_fn = model_path + '/' + (model_path.split('/'))[-1] + '.caffemodel'

# Patching model to be able to compute gradients.
# Note that you can also manually add "force_backward: true" line to "deploy.prototxt".

model = caffe.io.caffe_pb2.NetParameter()
text_format.Merge(open(net_fn).read(), model)
model.force_backward = True
open('tmp.prototxt', 'w').write(str(model))

net = caffe.Classifier('tmp.prototxt', param_fn,
                       mean = np.float32([104.0, 116.0, 122.0]), # ImageNet mean, training set dependent
                       channel_swap = (2,1,0)) # the reference model has channels in BGR order instead of RGB

if args.gpu:
    caffe.set_mode_gpu()
    caffe.set_device(0)

if args.keys:
    print net.blobs.keys()
    sys.exit()

# a couple of utility functions for converting to and from Caffe's input image layout
def preprocess(net, img):
    return np.float32(np.rollaxis(img, 2)[::-1]) - net.transformer.mean['data']
def deprocess(net, img):
    return np.dstack((img + net.transformer.mean['data'])[::-1])
def objective_L2(dst):
    dst.diff[:] = dst.data 

def make_step(net, step_size=1.5, end='inception_4c/output', 
              jitter=32, clip=True, objective=objective_L2):
    '''Basic gradient ascent step.'''

    src = net.blobs['data'] # input image is stored in Net's 'data' blob
    dst = net.blobs[end]

    ox, oy = np.random.randint(-jitter, jitter+1, 2)
    src.data[0] = np.roll(np.roll(src.data[0], ox, -1), oy, -2) # apply jitter shift
            
    net.forward(end=end)
    objective(dst)  # specify the optimization objective
    # dst.diff[:] = dst.data  # specify the optimization objective
    net.backward(start=end)
    g = src.diff[0]
    # apply normalized ascent step to the input image
    src.data[:] += step_size/np.abs(g).mean() * g

    src.data[0] = np.roll(np.roll(src.data[0], -ox, -1), -oy, -2) # unshift image
            
    if clip:
        bias = net.transformer.mean['data']
        src.data[:] = np.clip(src.data, -bias, 255-bias)

def deepdream(net, base_img, iter_n=10, octave_n=4, octave_scale=1.4, 
              end='inception_4c/output', clip=True, **step_params):
    # prepare base images for all octaves
    octaves = [preprocess(net, base_img)]
    for i in xrange(octave_n-1):
        octaves.append(nd.zoom(octaves[-1], (1, 1.0/octave_scale,1.0/octave_scale), order=1))
    
    src = net.blobs['data']
    detail = np.zeros_like(octaves[-1]) # allocate image for network-produced details
    for octave, octave_base in enumerate(octaves[::-1]):
        h, w = octave_base.shape[-2:]
        if octave > 0:
            # upscale details from the previous octave
            h1, w1 = detail.shape[-2:]
            detail = nd.zoom(detail, (1, 1.0*h/h1,1.0*w/w1), order=1)

        src.reshape(1,3,h,w) # resize the network's input image size
        src.data[0] = octave_base+detail
        print octave, end, iter_n,"..."
        for i in xrange(iter_n):
            make_step(net, end=end, clip=clip, **step_params)
            
            # visualization
            vis = deprocess(net, src.data[0])
            if not clip: # adjust image contrast if clipping is disabled
                vis = vis*(255.0/np.percentile(vis, 99.98))
            # showarray(vis)
            # print octave, i, end, vis.shape
            # clear_output(wait=True)
            
        # extract details produced on the current octave
        detail = src.data[0]-octave_base
    # returning the resulting image
    return deprocess(net, src.data[0])

def objective_guide(dst):
    global guide_features
    x = dst.data[0].copy()
    y = guide_features
    ch = x.shape[0]
    x = x.reshape(ch,-1)
    y = y.reshape(ch,-1)
    A = x.T.dot(y) # compute the matrix of dot-products with guide features
    dst.diff[0].reshape(ch,-1)[:] = y[:,A.argmax(1)] # select ones that match best

srcImage = PIL.Image.open(imgName).convert('RGB')
if not args.raw:
    (w, h) = srcImage.size
    if w > 1024 or h > 1024:
        srcImage.thumbnail((1024,1024),PIL.Image.ANTIALIAS)

img = np.float32(srcImage)

if args.kaleido:
    kaleid = PIL.Image.open(imgName)
    kaleid.thumbnail((224,224),PIL.Image.ANTIALIAS)
    guide = np.float32(kaleid)
    h, w = guide.shape[:2]
    src, dst = net.blobs['data'], net.blobs[args.end]
    src.reshape(1,3,h,w)
    src.data[0] = preprocess(net, guide)
    net.forward(end=args.end)
    guide_features = dst.data[0].copy()
    objective = objective_guide
elif args.guide != '':
    guide = np.float32(PIL.Image.open(args.guide))
    h, w = guide.shape[:2]
    src, dst = net.blobs['data'], net.blobs[args.end]
    src.reshape(1,3,h,w)
    src.data[0] = preprocess(net, guide)
    net.forward(end=args.end)
    guide_features = dst.data[0].copy()
    objective = objective_guide
else:
    objective = objective_L2

frame = deepdream(net, img, end=args.end, iter_n=args.iter, octave_scale=args.oscale, octave_n=args.octaves, objective=objective)
PIL.Image.fromarray(np.uint8(frame)).save(outName)

print "Elapsed: %.2f" % (time.time()-st)

comments = """
Observations


clouds_1024 at (20/6/4a) takes 88 secs  (CPU Only - need to figure out how to compile for GPU...)
clouds_1024 at (20/4/4a) takes 75 secs  (CPU Only - need to figure out how to compile for GPU...)
do_venice.sh (30/6/4a) clouds_1024 takes 153 (with one other dd process) 187 secs (with two other dd processes running)

512x281 image takes 12.3 secs
1024x563 image takes 46.48 per frame
3264x1794 image should takes approx 7 minutes

bvlc_google takes 55.76
Finetune_Flickr takes

Layer choice

'data',
 'conv1/7x7_s2',
 'pool1/3x3_s2',
 'pool1/norm1',
 'conv2/3x3_reduce',
 'conv2/3x3',
 'conv2/norm2',
 'pool2/3x3_s2',
 'pool2/3x3_s2_pool2/3x3_s2_0_split_0',
 'pool2/3x3_s2_pool2/3x3_s2_0_split_1',
 'pool2/3x3_s2_pool2/3x3_s2_0_split_2',
 'pool2/3x3_s2_pool2/3x3_s2_0_split_3',
 'inception_3a/1x1',
 'inception_3a/3x3_reduce',
 'inception_3a/3x3',
 'inception_3a/5x5_reduce',
 'inception_3a/5x5',
 'inception_3a/pool',
 'inception_3a/pool_proj',
 'inception_3a/output',
 'inception_3a/output_inception_3a/output_0_split_0',
 'inception_3a/output_inception_3a/output_0_split_1',
 'inception_3a/output_inception_3a/output_0_split_2',
 'inception_3a/output_inception_3a/output_0_split_3',
 'inception_3b/1x1',
 'inception_3b/3x3_reduce',
 'inception_3b/3x3',
 'inception_3b/5x5_reduce',      <-- STRIPES
 'inception_3b/5x5',
 'inception_3b/pool',
 'inception_3b/pool_proj',
 'inception_3b/output',
 'pool3/3x3_s2',
 'pool3/3x3_s2_pool3/3x3_s2_0_split_0',
 'pool3/3x3_s2_pool3/3x3_s2_0_split_1',
 'pool3/3x3_s2_pool3/3x3_s2_0_split_2',
 'pool3/3x3_s2_pool3/3x3_s2_0_split_3',
 'inception_4a/1x1',
 'inception_4a/3x3_reduce',
 'inception_4a/3x3',
 'inception_4a/5x5_reduce',       <-- SWIRLS
 'inception_4a/5x5',
 'inception_4a/pool',
 'inception_4a/pool_proj',
 'inception_4a/output',
 'inception_4a/output_inception_4a/output_0_split_0',
 'inception_4a/output_inception_4a/output_0_split_1',
 'inception_4a/output_inception_4a/output_0_split_2',
 'inception_4a/output_inception_4a/output_0_split_3',
 'inception_4b/1x1',
 'inception_4b/3x3_reduce',
 'inception_4b/3x3',
 'inception_4b/5x5_reduce',
 'inception_4b/5x5',
 'inception_4b/pool',
 'inception_4b/pool_proj',
 'inception_4b/output',
 'inception_4b/output_inception_4b/output_0_split_0',
 'inception_4b/output_inception_4b/output_0_split_1',
 'inception_4b/output_inception_4b/output_0_split_2',
 'inception_4b/output_inception_4b/output_0_split_3',
 'inception_4c/1x1',
 'inception_4c/3x3_reduce',
 'inception_4c/3x3',
 'inception_4c/5x5_reduce',
 'inception_4c/5x5',
 'inception_4c/pool',
 'inception_4c/pool_proj',
 'inception_4c/output',
 'inception_4c/output_inception_4c/output_0_split_0',
 'inception_4c/output_inception_4c/output_0_split_1',
 'inception_4c/output_inception_4c/output_0_split_2',
 'inception_4c/output_inception_4c/output_0_split_3',
 'inception_4d/1x1',
 'inception_4d/3x3_reduce',
 'inception_4d/3x3',
 'inception_4d/5x5_reduce',
 'inception_4d/5x5',
 'inception_4d/pool',
 'inception_4d/pool_proj',
 'inception_4d/output',
 'inception_4d/output_inception_4d/output_0_split_0',
 'inception_4d/output_inception_4d/output_0_split_1',
 'inception_4d/output_inception_4d/output_0_split_2',
 'inception_4d/output_inception_4d/output_0_split_3',
 'inception_4e/1x1',
 'inception_4e/3x3_reduce',
 'inception_4e/3x3',
 'inception_4e/5x5_reduce',
 'inception_4e/5x5',
 'inception_4e/pool',
 'inception_4e/pool_proj',
 'inception_4e/output',
 'pool4/3x3_s2',
 'pool4/3x3_s2_pool4/3x3_s2_0_split_0',
 'pool4/3x3_s2_pool4/3x3_s2_0_split_1',
 'pool4/3x3_s2_pool4/3x3_s2_0_split_2',
 'pool4/3x3_s2_pool4/3x3_s2_0_split_3',
 'inception_5a/1x1',
 'inception_5a/3x3_reduce',
 'inception_5a/3x3',
 'inception_5a/5x5_reduce',
 'inception_5a/5x5',
 'inception_5a/pool',
 'inception_5a/pool_proj',
 'inception_5a/output',
 'inception_5a/output_inception_5a/output_0_split_0',
 'inception_5a/output_inception_5a/output_0_split_1',
 'inception_5a/output_inception_5a/output_0_split_2',
 'inception_5a/output_inception_5a/output_0_split_3',
 'inception_5b/1x1',
 'inception_5b/3x3_reduce',
 'inception_5b/3x3',
 'inception_5b/5x5_reduce',
 'inception_5b/5x5',
 'inception_5b/pool',
 'inception_5b/pool_proj',
 'inception_5b/output',
 'pool5/7x7_s1',
 'loss3/classifier',
 'prob'



"""
