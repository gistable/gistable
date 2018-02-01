'''
If you allways endup googleing how to code down relative paths inside django's 
settings.py file using the os.path module, you should consider bookmarking this
code snippet

Usage inside settings.py:
    SITE_ROOT = site_root_path(__file__)
    .
    .
    .
    MEDIA_ROOT = join_path(SITE_ROOT, "media")
    TEMPLATE_DIRS = (
        join_path(SITE_ROOT,"templates"),
    )
    
'''

import os

def site_root_path(settings_file_path):
    '''
    @param settings_file_path: __file__ attribute
    @return: /path/to/your/django_project
    '''
    return os.path.dirname(os.path.realpath(settings_file_path))

def join_path(*args):
    '''@return: arg1/arg2'''
    return os.path.join(*args)