from io import BytesIO
import requests
from django.core.files.images import ImageFile
from wagtail.wagtailimages.models import Image

# event is a model object, substitute your model
# filename and title are up to you
# in my model, event.event_image is a ForeignKey to wagtailimages.Image

response = requests.get(url)
image = Image(title=title, file=ImageFile(BytesIO(response.content), name=filename))
image.save()
event.event_image = image
event.save()