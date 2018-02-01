def reload_urlconf(urlconf=None, urls_attr='urlpatterns'):
    if urlconf is None:
        urlconf = settings.ROOT_URLCONF
        if urlconf in sys.modules:
            reload(sys.modules[urlconf])
    reloaded = import_module(urlconf)
    reloaded_urls = getattr(reloaded, urls_attr)
    set_urlconf(tuple(reloaded_urls))