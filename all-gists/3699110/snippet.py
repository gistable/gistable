import os
import urllib2
import contextlib
import StringIO

from django.core.files.storage import get_storage_class, FileSystemStorage
from django.core.files import File
from django.conf import settings

from galleries.models import GalleryImage

OLD_STORAGE = FileSystemStorage()
NEW_STORAGE = get_storage_class(settings.REMOTE_FILE_STORAGE)()


def save_local_file(local_path):
    with open(local_path) as file:
        fn = os.path.split(local_path)[1]
        django_file = File(file, fn)
        path = NEW_STORAGE.save(fn, django_file)
        print local_path, 'saved to', path
        # save path

def save_from_url(url):
    with contextlib.closing(urllib2.urlopen(url)) as response:
        with contextlib.closing(StringIO.StringIO(response)) as file:
            file.seek(0)

            fn = os.path.split(url)[1]
            django_file = File(file, fn)

            path = NEW_STORAGE.save(fn, django_file)
            # with an object this would be
            # obj.image_field.save(fn, file)

            print url, 'saved to', path

save_local_file('pip-log.txt')
save_from_url('http://static.bbci.co.uk/frameworks/barlesque/2.8.11/desktop/3.5/img/blq-blocks_grey_alpha.png')