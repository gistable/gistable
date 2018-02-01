import base64
import cStringIO

from django.core.files.uploadedfile import InMemoryUploadedFile

# ...
if request.POST.get('file') and request.POST.get('name'):
    file = cStringIO.StringIO(base64.b64decode(request.POST['file']))
    image = InMemoryUploadedFile(file,
       field_name='file',
       name=request.POST['name'],
       content_type="image/jpeg",
       size=sys.getsizeof(file),
       charset=None)
request.FILES[u'file'] = image
# ...