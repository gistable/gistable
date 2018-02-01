import urlparse
import re
from django.db import models
from django import  forms


def validate_youtube_url(value):
    '''El patron lo saque de http://stackoverflow.com/questions/2964678/jquery-youtube-url-validation-with-regex'''
    pattern = r'^http:\/\/(?:www\.)?youtube.com\/watch\?(?=.*v=\w+)(?:\S+)?$'

    if value[:16] == 'http://youtu.be/':
        if re.match(r'\w+', value[16:]) is None:
            raise forms.ValidationError(_('Not a valid Youtube URL'))
    elif re.match(pattern, value) is None:
        raise forms.ValidationError(_('Not a valid Youtube URL'))


class YoutubeUrl(unicode):
    @property
    def video_id(self):
        parsed_url = urlparse.urlparse(self)
        if parsed_url.query == '':
            return parsed_url.path
        return urlparse.parse_qs(parsed_url.query)['v'][0]

    @property
    def embed_url(self):
        return 'http://youtube.com/embed/%s/' % self.video_id

    @property
    def thumb(self):
        return "http://img.youtube.com/vi/%s/2.jpg" % self.video_id




class YoutubeUrlField(models.URLField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        super(YoutubeUrlField, self).__init__(*args, **kwargs)
        self.validators.append(validate_youtube_url)

    def to_python(self, value):

        url = super(YoutubeUrlField, self).to_python(value)

        return YoutubeUrl(url)

    def get_prep_value(self, value):
        return unicode(value)



try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([],  ["^fields\.YoutubeUrlField"])
except ImportError:
    pass
