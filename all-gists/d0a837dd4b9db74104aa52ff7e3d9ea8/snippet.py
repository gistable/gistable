from django.apps import AppConfig


class CMSConfig(AppConfig):
    name = 'myproj.apps.cms'

    def ready(self):
        from wagtail.wagtailcore.models import Site

        root_paths = Site.get_site_root_paths()
        Site.get_site_root_paths = lambda: root_paths