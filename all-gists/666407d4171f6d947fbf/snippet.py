class Observable(object):
    """Mixin for use cases that can fire events to be handled by observers"""
    
    def __init__(self):
        self._observers = []
    
    def attach_observer(self, observer):
        self._observers.append(observer)
    
    def notify_observers(self, event, *args, **kwargs):
        for observer in self._observers:
            if hasattr(observer, event):
                getattr(observer, event)(*args, **kwargs)


class SiteRegistryObserver(object):
    """Watch for user created site event and register site"""
    
    def __init__(self, site_registry=SiteRegistry):
        self.site_registry = site_registry()
        
    def user_created_site(self, user, site):
        self.site_registry.add_site(user, site)


class SiteServiceObserver(object):
    """Watch for user created site event and add to site service"""
    
    def __init__(self, site_service=SiteService):
        self.site_service = site_service()
    
    def user_created_site(self, user, site):
        self.site_service.add_site(user, site)


class UserCreatesSite(Observable):
    """Use case for user creating a site. Fires user_created_site event."""
    
    def __init__(self, user, data, model=Site):
        self.user = user
        self.site = model(**data)
    
    def perform(self):
        try:
            self.site.save()
            self.notify_observers("user_created_site", user=user, site=site)
        rescue IntegrityError as error:
            self.notify_observers("create_failed", error)
        

class SiteApi(ApiView):
    def create(self, request):
        """API endpoint for user creating site"""
        action = UserCreatesSite(request.user, request.DATA)
        action.attach_observer(SiteRegistryObserver())
        action.attach_observer(SiteServiceObserver())
        action.attach_observer(self)
        action.perform()
    
    def create_failed(self, reason):
        raise status.HTTP_400_BAD_REQUEST(reason)