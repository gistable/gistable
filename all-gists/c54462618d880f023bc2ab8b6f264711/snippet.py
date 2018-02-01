from skimage.transform import resize
class DualFlowGenerators(object):
    """
    Class to deliver X from multiple keras NumpyIterators.
    
    Can also resize the image    
    """
    def __init__(self, image_data_generators, resize=False):
        super().__init__()
        assert [a.n==image_data_generators[0].n for a in image_data_generators], 'all inputs should have same length'
        self.image_data_generators = image_data_generators
        self.resize = resize
        self.n = self.image_data_generators[0].n
        self.batch_size = self.image_data_generators[0].batch_size
        self.steps = int(self.n/self.batch_size)
        self.zipped = zip(*image_data_generators)
        
    def __next__(self):
        out = next(self.zipped)
        if self.resize:
            out = [[resize(image, output_shape=self.resize+(image.shape[-1],), mode='constant') for image in batch] for batch in out]
            out = np.array(out)
        return out
    
    def __iter__(self):
        return self.__next__()


# Usage:
from keras.preprocessing.image import ImageDataGenerator
import h5py
from keras.utils.io_utils import HDF5Matrix


# we create two instances with the same arguments
data_gen_args = dict(
    rotation_range=90.,
    width_shift_range=0.05,
    height_shift_range=0.05,
    zoom_range=0.2,
    channel_shift_range=0.005,
    horizontal_flip=True,
    vertical_flip=True,
    fill_mode='constant',
    data_format="channels_last",
)
image_datagen = ImageDataGenerator(**data_gen_args)
mask_datagen = ImageDataGenerator(**data_gen_args)

X_train = HDF5Matrix(os.path.join(out_dir, 'train_X_3band.h5'), 'X')
y_train = HDF5Matrix(os.path.join(out_dir, 'train_y_3class.h5'), 'y')

image_generator = image_datagen.flow(
    X_train, None, 
    seed=seed, 
    batch_size=batch_size,
)
mask_generator = mask_datagen.flow(
    y_train, None,
    seed=seed,
    batch_size=batch_size,
)

# combine generators into one which yields image and masks
train_generator = DualFlowGenerators([image_generator, mask_generator], resize=(224,224))
train_generator

X, y = next(train_generator)
X.shape, y.shape