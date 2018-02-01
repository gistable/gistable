import uuid

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, Transpose, SmartResize

def get_file_path(instance, filename):
  ext = filename.split('.')[-1]
  filename = "%s.%s" % (uuid.uuid4(), ext)
  return os.path.join('upload/images/avatar', filename)

class UserProfile(models.Model):
  avatar = models.ImageField(upload_to=get_file_path, max_length=255, blank=True, null=True)
  avatar_thumbnail = ImageSpecField(
    source='avatar',
    processors = [Transpose(),SmartResize(200, 200)],
    format = 'JPEG',
    options = {'quality': 80}
  )
  
  def profile_image_url(self):
    return "{}".format(self.user.profile.avatar_thumbnail.url)