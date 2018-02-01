# UpYun storage for django, written by Tyr Chen @ tukeq.com
# to run this gist you need to get upyun python sdk first.

# upyun storage
class UpYunStorage(Storage):
  def __init__(self, bucket=settings.UPYUN_BUCKET):
    self.upyun = UpYun(bucket, settings.UPYUN_USERNAME, settings.UPYUN_PASSWORD)
    self.upyun.setApiDomain(settings.UPYUN_API_DOMAIN)
    self.binding_domain = settings.UPYUN_BINDING_DOMAIN


  def _open(self, name, mode='rb'):
    class UpYunFile(File):
      def __init__(self, name, upyun):
        self.name = name
        self.upyun = upyun

      def size(self):
        info = self.upyun.getFileInfo(name)
        if info:
          return info['size']
        return 0

      def read(self, *args, **kwargs):
        return self.upyun.readFile(self.name)

      def write(self, data):
        return self.upyun.writeFile(self.name, data)

      def close(self):
        return

    return UpYunFile(name, self.upyun)

  def _save(self, name, content):
    self.upyun.writeFile(name, content)
    return name

  def delete(self, name):
    self.upyun.deleteFile(name)

  def exists(self, name):
    return self.upyun.getFileInfo(name) != None

  def listdir(self, path):
    return [d.filename for d in self.upyun.readDir(path)]

  def path(self, name):
    raise NotImplementedError

  def size(self, name):
    info = self.upyun.getFileInfo(name)
    if info:
      return int(info['size'])
    return 0

  def url(self, name):
    return urljoin(self.binding_domain, name)

  def get_available_name(self, name):
    return name


def get_upload_to(instance, filename):
  import os, uuid
  return '%s%s' % (uuid.uuid4().hex, os.path.splitext(filename)[1])

def set_storage(bucket):
  if settings.USE_UPYUN:
    return UpYunStorage(bucket)
  return None

def set_upload_to(upload_to=''):
  if not upload_to:
    return get_upload_to
  return upload_to


class UpYunFileField(models.FileField):
  def __init__(self, bucket=settings.UPYUN_BUCKET, verbose_name=None, name=None, upload_to='', **kwargs):
    storage = set_storage(bucket)
    upload_to = set_upload_to(upload_to)
    super(UpYunFileField, self).__init__(verbose_name, name, upload_to, storage, **kwargs)


# usage:
# just add UpYunFileField into your model, and the storage will do the magic. You need to setup several consts in settings to make UpYun storage
# work. Good luck.