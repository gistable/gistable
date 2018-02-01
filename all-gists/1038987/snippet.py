# Example usage:
# with temporary_settings(CELERY_ALWAYS_EAGER=True):
#     run_task.delay() # runs task with eager setting enabled.

from contextlib import contextmanager
from django.conf import settings

@contextmanager
def temporary_settings(**temp_settings):
    orig_settings = {}
    for key, value in temp_settings.iteritems():
        if hasattr(settings, key):
            orig_settings[key] = getattr(settings, key)
        setattr(settings, key, value)
    yield
    for key, value in temp_settings.iteritems():
        if orig_settings.has_key(key):
            setattr(settings, key, orig_settings[key])
        else:
            delattr(settings, key)