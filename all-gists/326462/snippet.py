
from PIL import Image

class ThumbNail(object):

    """
    init function for base Class
    Parameters
    ------------
    targetFile:
        the original file (string)
    newFile
        thumbnail file that will be created (string)
    sizes:
        width and height of thumbnail. (tuple)
    ratio:
        if it's False, thumbnail will be created as exactly
        with your sizes. if you pass it as True, thumbnail sizes will be
        preserve original file's height/width ratio.
        default value of this parameter is "False".

    """
    def __init__(self, targetFile, newFile, sizes, ratio = False):
        self.targetFile = targetFile
        self.newFile    = newFile
        self.sizes      = sizes
        self.ratio      = ratio

        if self.ratio == True:
            self.thumbnailWithRatio()
        else:
            self.thumbnail()

    def thumbnail(self):

        self.im = Image.open(self.targetFile)
        orig_width, orig_height   = self.im.size
        thumb_width, thumb_height = self.sizes
        orig_ratio, thumb_ratio   = float(orig_width) / float(orig_height), float(thumb_width) / float(thumb_height)

        if thumb_ratio < orig_ratio:
            crop_height = orig_height
            crop_width  = crop_height * thumb_ratio
            x_offset = float(orig_width - crop_width) / 2
            y_offset = 0
        else:
            crop_width = orig_width
            crop_height = crop_width / thumb_ratio
            x_offset = 0
            y_offset = float(orig_height - crop_height) / 3

        # cropping process
        self.im = self.im.crop((x_offset, y_offset, x_offset+int(crop_width), y_offset+int(crop_height)))
        self.im = self.im.resize((thumb_width, thumb_height), Image.ANTIALIAS)
        self.im.save(self.newFile)

    def thumbnailWithRatio(self):
        self.im = Image.open(self.targetFile)
        self.im.thumbnail(self.sizes, Image.ANTIALIAS)
        self.im.save(self.newFile)


import glob
for item in glob.glob("*.jpg"):
    ThumbNail(item, item + "-o.jpg", (600, 800), True)
    ThumbNail(item, item + "-p.jpg", (100, 100), False)
