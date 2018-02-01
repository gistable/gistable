import os
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from PIL import Image
from PIL.ExifTags import TAGS
from cStringIO import StringIO


def orientation_rotation(im):
    #take pil Image insctance and if need rotate it
    orientation = None
    try:
        exifdict = im._getexif()
    except AttributeError:
        exifdict = {}
    if exifdict:
        for k in exifdict.keys():
            if k in TAGS.keys():
                if TAGS[k] == 'Orientation':
                   orientation =  exifdict[k]
    if orientation in (3, 6, 8):
        if orientation == 6:
            im = im.rotate(-90)
        elif orientation == 8:
            im = im.rotate(90)
        elif orientation == 3:
            im = im.rotate(180)
    return im

def rotate_in_memory(image):
    #take inmemory file and return rotated(if need) Inmemory file
    image.seek(0)
    f = StringIO(image.read()) #user image
    img = StringIO() #result image
    im = Image.open(f) #PIL processing image
    im = orientation_rotation(im)
    im.save(img, 'JPEG')
    img.seek(0, os.SEEK_END)
    img_len = img.tell()
    img.seek(0)
    return InMemoryUploadedFile(img, image.field_name, image.name, image.content_type, img_len, image.charset)

def rotate_temporary(image):
    #take temporary file and return rotated(if need) temporary file
    file_path = image.temporary_file_path()
    im = Image.open(file_path)
    im = orientation_rotation(im)
    im.save(file_path, 'JPEG')
    return image

def fix_photo_orientation(image):
    if isinstance(image, InMemoryUploadedFile):
        image = rotate_in_memory(image)
    if isinstance(image, TemporaryUploadedFile):
        image = rotate_temporary(image)
    return image

#usage: fix_photo_orientation(image)
