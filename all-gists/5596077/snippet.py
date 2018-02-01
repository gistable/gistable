from mincepie import mapreducer, launcher
import gflags
import glob
import leargist
import numpy as np
import os
from PIL import Image
import uuid
 
# constant value
GIST_DIM = 960
GIST_DTYPE = np.float32
 
# gflags
gflags.DEFINE_string("input_folder", "",
                     "The folder that contains all input images, organized in synsets.")
gflags.DEFINE_string("output_folder", "",
                     "The folder that we write output features to")
FLAGS = gflags.FLAGS
 
 
def process_image(filename, max_size=256):
    """Takes an image name and computes the gist feature
    """
    im = Image.open(filename)
    im.thumbnail((max_size, max_size), Image.ANTIALIAS)
    return leargist.color_gist(im)
 
 
class PygistMapper(mapreducer.BasicMapper):
    """The ImageNet Compute mapper. The input value would be a synset name.
    """
    def map(self, key, value):
        if type(value) is not str:
            value = str(value)
        files = glob.glob(os.path.join(FLAGS.input_folder, value, '*.JPEG'))
        files.sort()
        features = np.zeros((len(files), GIST_DIM), dtype = GIST_DTYPE)
        for i, f in enumerate(files):
            try:
                feat = process_image(f)
                features[i] = feat
            except Exception, e:
                # we ignore the exception (maybe the image is corrupted or
                # pygist has some bugs?)
                print f, Exception, e
        outname = str(uuid.uuid4()) + '.npy'
        np.save(os.path.join(FLAGS.output_folder, outname), features)
        yield value, outname
 
mapreducer.REGISTER_DEFAULT_MAPPER(PygistMapper)
 
 
class PygistReducer(mapreducer.BasicReducer):
    def reduce(self, key, values):
        """The Reducer basically renames the numpy file to the synset name
        Input:
            key: the synset name
            value: the temporary name from map
        """
        os.rename(os.path.join(FLAGS.output_folder, values[0]),
                os.path.join(FLAGS.output_folder, key + '.npy'))
        return key
 
 
mapreducer.REGISTER_DEFAULT_REDUCER(PygistReducer)
mapreducer.REGISTER_DEFAULT_READER(mapreducer.FileReader)
mapreducer.REGISTER_DEFAULT_WRITER(mapreducer.FileWriter)
 
if __name__ == "__main__":
    launcher.launch()