import os

from django.conf import settings
from django.contrib.staticfiles.finders import BaseFinder, AppDirectoriesFinder
from django.contrib.staticfiles.storage import AppStaticStorage
from django.core.files.storage import FileSystemStorage
from django.utils._os import safe_join


class AppMediaStorage(AppStaticStorage):
    source_dir = 'media'


class MediaFinder(AppDirectoriesFinder):
    storage_class = AppMediaStorage


class MediaRootFinder(BaseFinder):
    """
    Since the static files runserver can not find media definitions, it is now
    added by this finder. This way you don't have to define anything in urls.py
    to make django server both static and media files.
    """
    def find(self, path, all=False):
        """
        Looks for files in the MEDIA_ROOT
        """
        media_prefix = settings.MEDIA_URL.replace(settings.STATIC_URL, '')
        if  path.startswith(media_prefix):
            location = safe_join(settings.STATIC_ROOT, path)
            if os.path.exists(location):
                if not all:
                    return location
                return [location]
        
        return []
    
    def list(self, ignore_patterns):
        """
        List all files in all locations.
        """
        yield settings.MEDIA_ROOT, FileSystemStorage()
