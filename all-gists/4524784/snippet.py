import inspect
from django.conf import settings
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class Registry(object):
    "Simple class that keeps track of a set of registered classes."
    def __init__(self, default=None, register_instance=True):
        if register_instance and inspect.isclass(default):
            default = default()
        self.register_instance = register_instance
        self.default = default
        self._registry = {}
        if default:
            self.register(default)

    def __getitem__(self, name):
        return self._registry.get(name, self.default)

    def get(self, name):
        return self.__getitem__(name)

    def register(self, obj, name=None):
        """Registers a class with an optional name. The class name will be used
        if not supplied.
        """
        if inspect.isclass(obj):
            name = name or obj.__name__
            # Create an instance if instances should be registered
            if self.register_instance:
                obj = obj()
        else:
            name = name or obj.__class__.__name__

        if name in self._registry:
            raise AlreadyRegistered('The class {0} is already registered'.format(name))

        # Check to see if this class should be used as the default for this
        # registry
        if getattr(obj, 'default', False):
            # ensure the default if already overriden is not being overriden
            # again.
            if self.default:
                if self.register_instance:
                    name = self.default.__class__.__name__
                else:
                    name = self.default.__name__
                objtype = 'class' if self.register_instance else 'instance'
                raise ImproperlyConfigured('The default {0} cannot be set '
                    'more than once for this registry ({1} is the default).'.format(objtype, name))

            self.default = obj
        else:
            if name in self._registry:
                raise AlreadyRegistered('Another class is registered with the '
                    'name "{0}"'.format(name))

            self._registry[name] = obj

    def unregister(self, name):
        """Unregisters a class. Note that these calls must be made in
        INSTALLED_APPS listed after the apps that already registered the class.
        """
        # Use the name of the class if passed in. Second condition checks for an
        # instance of the class.
        if inspect.isclass(name):
            name = name.__name__
        elif hasattr(name, '__class__'):
            name = name.__class__.__name__
        if name not in self._registry:
            objtype = 'class' if self.register_instance else 'instance'
            raise NotRegistered('No {0} is registered under the name "{1}"'.format(objtype, name))
        self._registry.pop(name)

    @property
    def choices(self):
        "Returns a 2-tuple list of all registered class instance names."
        return sorted((x, x) for x in self._registry.iterkeys())


def autodiscover(module_name):
    """Simple auto-discover for looking through each INSTALLED_APPS for each
    ``module_name`` and fail silently when not found. This should be used for
    modules that have 'registration' like behavior.
    """
    for app in settings.INSTALLED_APPS:
        # Attempt to import the app's ``module_name``.
        try:
            import_module('{0}.{1}'.format(app, module_name))
        except:
            pass