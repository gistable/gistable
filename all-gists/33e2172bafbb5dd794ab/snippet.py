# Authors: Kyle Kastner, Francesco Visin
# License: BSD 3-Clause
try:
    import Queue
except ImportError:
    import queue as Queue
import threading
import time
from matplotlib.path import Path
from PIL import Image
import numpy as np
import warnings
import os
import itertools
from retrying import retry
# Get pycocotools from https://github.com/pdollar/coco/archive/master.zip
# Go to coco-master/PythonAPI
# python setup.py build
# python setup.py install
from pycocotools.coco import COCO
from pycocotools import mask as cocomask


def fetch_from_COCO(filenames, img_list,
                    coco_info,
                    resize_images=False, resize_size=-1,
                    load_categories=['person']):
    images = []
    masks = []
    assert len(filenames) == len(img_list)
    for n, img_el in enumerate(img_list):
        # load image
        if not os.path.exists(filenames[n]):
            print('Image %s is missing' % filenames[n])
            continue

        pth = filenames[n]
        im = Image.open(pth)

        coco, catIds, imgIds = coco_info

        # load the annotations and build the mask
        anns = coco.loadAnns(coco.getAnnIds(
            imgIds=img_el['id'], catIds=catIds, iscrowd=None))

        mask = np.zeros(im.size).transpose(1, 0)
        for ann in anns:
            catId = ann['category_id']
            if type(ann['segmentation']) == list:
                # polygon
                for seg in ann['segmentation']:
                    # xy vertex of the polygon
                    poly = np.array(seg).reshape((len(seg)/2, 2))
                    closed_path = Path(poly)
                    nx, ny = img_el['width'], img_el['height']
                    x, y = np.meshgrid(np.arange(nx),
                                       np.arange(ny))
                    x, y = x.flatten(), y.flatten()
                    points = np.vstack((x, y)).T
                    grid = closed_path.contains_points(points)
                    if np.count_nonzero(grid) == 0:
                        warnings.warn(
                            'One of the annotations that compose the mask '
                            'of %s was empty' % img_el['file_name'],
                            RuntimeWarning)
                    grid = grid.reshape((ny, nx))
                    mask[grid] = catId
            else:
                # mask
                if type(ann['segmentation']['counts']) == list:
                    rle = cocomask.frPyObjects(
                        [ann['segmentation']],
                        img_el['height'], img_el['width'])
                else:
                    rle = [ann['segmentation']]
                grid = cocomask.decode(rle)[:, :, 0]
                grid = grid.astype('bool')
                mask[grid] = catId

        # zero_pad
        if resize_images:
            rx, ry = resize_size
            # resize (keeping proportions)
            [x, y] = im.size
            dx = float(rx)/x
            dy = float(ry)/y
            ratio = min(dx, dy)
            x = int(x * ratio)
            y = int(y * ratio)

            # workaround for PIL problems..
            @retry(stop_max_attempt_number=7, wait_fixed=2000)
            def res(im, x, y):
                return im.resize((x, y), Image.ANTIALIAS)
            im = res(im, x, y)
            # mask = mask / numpy.max(mask) * 255.0 --> only visualization
            mask = Image.fromarray(mask.astype('uint8'))
            mask = mask.resize((x, y), Image.NEAREST)

            tmp = im
            im = Image.new("RGB", (rx, ry))
            im.paste(tmp, ((rx-x)/2, (ry-y)/2))
            tmp = mask
            # 80 obj categories
            mask = Image.new("L", (rx, ry))
            mask.paste(tmp, ((rx-x)/2, (ry-y)/2))

            images.append(np.asarray(im))
            masks.append(np.asarray(mask))
    return images, masks, filenames


class COCOThread(threading.Thread):
    """Image Thread"""
    def __init__(self, queue, out_queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.out_queue = out_queue

    def run(self):
        while True:
            # Grabs image path from queue
            filenames, image_list, coco_info = self.queue.get()
            try:
                # Grab image
                # print('reading image', image_path)
                image_group, mask_group, filenames = fetch_from_COCO(
                    filenames, image_list, coco_info)
                # Place image in out queue
                self.out_queue.put((image_group, mask_group))
                # Signals to queue job is done
                self.queue.task_done()
            except IOError:
                print("Image in image_group corrupted!")
                print(image_group)


class MSCOCO_dataset(object):
    def __init__(self, minibatch_size=3, which_set="train", coco_path="/data/lisa/data/COCO/",
                 load_categories=['person']):
        if which_set == "train":
            partial_path = "train2014"
        elif which_set == "valid":
            partial_path = "val2014"
        elif which_set == "test2014":
            partial_path = "test2014"
        elif which_set == "test2015":
            partial_path = "test2015"
        else:
            raise ValueError("Unknown setting for which_set %s" % which_set)

        base_path = os.path.join(coco_path, "images", partial_path)
        ann_path = '%s/annotations_v1.0.3/instances_%s.json' % (coco_path,
                                                                partial_path)
        filenames = []
        # initialize COCO api for instance annotations
        coco = COCO(ann_path)

        # get all images containing the given categories
        catIds = coco.getCatIds(catNms=load_categories)
        imgIds = coco.getImgIds(catIds=catIds)
        img_list = coco.loadImgs(imgIds)

        self.coco_info = (coco, catIds, imgIds)
        for img_el in img_list:
            # load image
            filename = '%s/%s' % (base_path, img_el['file_name'])
            if not os.path.exists(filename):
                print('Image %s is missing' % img_el['file_name'])
            else:
                filenames.append(filename)

        assert(len(filenames) == len(img_list))
        self.image_list = img_list
        self.filenames = filenames

        self.n_per_epoch = len(filenames)
        self.n_samples_seen_ = 0

        # Test random order
        # random.shuffle(self.image_paths)

        self.buffer_size = 5
        self.minibatch_size = minibatch_size
        self.input_qsize = 50
        self.min_input_qsize = 10
        if len(self.image_list) % self.minibatch_size != 0:
            print("WARNING: Sample size not an even multiple of minibatch size")
            print("Truncating...")
            self.image_list = self.image_list[:-(
                len(self.image_list) % self.minibatch_size)]
            self.filenames = self.filenames[:-(
                len(self.filenames) % self.minibatch_size)]
        assert len(self.image_list) % self.minibatch_size == 0
        assert len(self.filenames) % self.minibatch_size == 0

        self.grouped_image_list = zip(*[iter(self.image_list)] *
                                      self.minibatch_size)
        self.grouped_filenames = zip(*[iter(self.filenames)] *
                                     self.minibatch_size)
        # Infinite...
        self.grouped_elements = itertools.cycle(zip(self.grouped_filenames,
                                                self.grouped_image_list,
                                                [self.coco_info] * len(
                                                    self.grouped_image_list)))
        self.queue = Queue.Queue()
        self.out_queue = Queue.Queue(maxsize=self.buffer_size)
        self._init_queues()

    def _init_queues(self):
        for i in range(1):
            self.it = COCOThread(self.queue, self.out_queue)
            self.it.setDaemon(True)
            self.it.start()

        # Populate queue with some paths to image data
        for n, _ in enumerate(range(self.input_qsize)):
            group = self.grouped_elements.next()
            self.queue.put(group)

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        return self._step()

    def reset(self):
        self.n_samples_seen_ = 0

    def _step(self):
        if self.n_samples_seen_ >= self.n_per_epoch:
            self.reset()
            raise StopIteration("End of epoch")
        image_group = self.out_queue.get()
        self.n_samples_seen_ += self.minibatch_size
        if self.queue.qsize() <= self.min_input_qsize:
            for image_path_group in range(self.input_qsize):
                group = self.grouped_elements.next()
                self.queue.put(group)
        return image_group


if __name__ == "__main__":
    # Example usage
    ds = MSCOCO_dataset()
    start = time.time()
    n_minibatches_to_run = 100
    itr = 1
    while True:
        image_group = ds.next()
        # time.sleep approximates running some model
        time.sleep(1)
        stop = time.time()
        tot = stop - start
        print("Threaded time: %s" % (tot))
        print("Minibatch %s" % str(itr))
        print("Time ratio (s per minibatch): %s" % (tot / float(itr)))
        itr += 1
        # test
        if itr >= n_minibatches_to_run:
            break
