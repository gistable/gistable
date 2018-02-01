from django.contrib.auth.models import User, SiteProfileNotAvailable
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models.signals import post_init
from django.dispatch.dispatcher import receiver


@receiver(post_init, sender=User)
def user_post_init(sender, instance, **kwargs):
    def get_profile():
        user = instance
        if not hasattr(user, '_profile_cache'):
            from django.conf import settings
            if not getattr(settings, 'AUTH_PROFILE_MODULE', False):
                raise SiteProfileNotAvailable('You need to set AUTH_PROFILE_MODULE in your project settings')
            try:
                app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
            except ValueError:
                raise SiteProfileNotAvailable('app_label and model_name should be separated by a dot in the AUTH_PROFILE_MODULE setting')

            try:
                model = models.get_model(app_label, model_name)
                if model is None:
                    raise SiteProfileNotAvailable('Unable to load the profile model, check AUTH_PROFILE_MODULE in your project settings')
                user._profile_cache, _ = model._default_manager.using(user._state.db).get_or_create(user=user)
                user._profile_cache.user = user
            except (ImportError, ImproperlyConfigured):
                raise SiteProfileNotAvailable
        return user._profile_cache

    instance.get_profile = get_profile
