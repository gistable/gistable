from PIL import Image as PILImage
import os
from django.core.files import File
from django.core.files.base import ContentFile
from cStringIO import StringIO

def create_thumbnail_from_image_field(image_field, thumbnail_image_field,
                                      thumb_width, thumb_height):
    """
    This function is intended to be used with a model similar to
    class UserProfile(models.Model):
        ...
        profile_pic = models.ImageField()
        profile_pic_thumb = models.ImageField()

    The profile_pic field is pre-populated eg. via user upload.
    The thumbnail field is then generated using this function as:
    THUMB_WIDTH = THUMB_HEIGHT = 48
    create_thumbnail_from_image_field(profile.profile_pic, profile.profile_pic_thumb, 
                                      THUMB_WIDTH, THUMB_HEIGHT)
    """
    # open the image_field file to allow PIL to read from it
    image_field.open(mode='rb')

    # process the image_field to genearate a thumbnail
    img = PILImage.open(image_field)
    thumbimg = img.copy()
    thumbimg.thumbnail((thumb_width, thumb_height), PILImage.ANTIALIAS)

    # save the thumbnail to memory
    mem_thumb = StringIO()
    thumbimg.save(mem_thumb, 'png')
    mem_thumb.seek(0)
    
    # figure out the filename for the thumbnail based on the filename of the
    # profile pic
    path, image_basename = os.path.split(image_field.name)
    frontname, ext = os.path.splitext(image_basename)
    thumb_basename = frontname + '_thumb.png' # thumbs always saved as png

    # save the thumbnail data to the actual file managed by the field
    thumbnail_image_field.save(thumb_basename,
                               ContentFile(mem_thumb.read()), save=False)