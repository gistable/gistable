class ReloaderEventHandler(FileSystemEventHandler):
    """
    Listen for changes to modules within the Django project
    On change, reload the module in the Python Shell

    Custom logic required to reload django models.py modules
    Due to the singleton AppCache, which caches model references.
    For those models files, we must clear and repopulate the AppCache
    """
    def __init__(self, *args, **kwargs):
        self.project_root = kwargs.pop('project_root', None)
        self.shell_globals = kwargs.pop('shell_globals', None)
        self.model_globals = kwargs.pop('model_globals', None)
        super(ReloaderEventHandler, self).__init__(*args, **kwargs)

    def dispatch(self, event):
        event_path = event.src_path
        path, file_extension = os.path.splitext(event_path)
        if all([
                file_extension == '.py',
                'shell_plus' not in path,
                self.project_root in path
                ]):

            return super(ReloaderEventHandler, self).dispatch(event)

    def on_created(self, event):
        super(ReloaderEventHandler, self).on_created(event)
        self._force_reload(event)

    def on_modified(self, event):
        """
        Called by dispatch on modification of file in the Django project
        """
        super(ReloaderEventHandler, self).on_modified(event)
        self._force_reload(event)

    def _force_reload(self, event):
        """
        Reload the altered module
        models.py files and all other python files are handled differently
        This is because models are cached by Django in a singleton
        We need to clear this singleton to properly reload
        """
        cleaned_path = self._clean_path(event.src_path)
        path_components = cleaned_path.split(os.path.sep)
        if path_components[-1] == 'models':
            self._reload_models_module(path_components[-2])
            # This redundant call bizarrely seems necessary
            # Issue exists around recompiling models.pyc file on 1st attempt
            # Subsequent reloads always work
            # time.sleep(1)
            self._reload_models_module(path_components[-2])
        else:
            self._reload_module(path_components)

    def _clean_path(self, path):
        """Remove the leading project path"""
        project_root = self.project_root if self.project_root.endswith('/') else "{}/".format(self.project_root)
        path_from_project_root = path.replace(project_root, '')
        # Remove trailing ".py" from module for importing purposes
        return os.path.splitext(path_from_project_root)[0]

    def _reload_module(self, path_components):
        """
        Wrapper for __builtin__ reload() function
        In addition to reloading the module,
        we reset the associated classes in the global scope of the shell.

        Consequently, we don't have to manaully reimport (i.e. 'from app import MyClass')
        Instead, MyClass will have changed for us automagically

        More interestingly, we also dynamically update the classes
        of existing object instances in the global scope with `_update_class_instances`.

        ## In a Shell session
        obj = MyKLS()
        obj.getchar() --> 'a'

        ## While still in the Shell,
        ### We change the function definition of getchar() in the filesytem to return 'b'
        ### In our Shell, we will see that

        obj.getchar() --> 'b'

        This behavior is very experimental and possibly dangerous but powerful
        Cuts down time and frustration during pdb debugging
        """

        # We attempt to import the module from the project root
        # This SHOULD be agnostic of app/project structure
        while True:
            try:
                module = importlib.import_module('.'.join(path_components))
            except ImportError:
                path_components.pop(0)
                if not path_components:
                    return
            else:
                break

        reload(module)
        # Reload objects into the global scope
        # This has the potential to cause namespace collisions
        # The upside is that we don't have to reimport (i.e. from module import ObjName)
        for attr in dir(module):
            if (
                not(attr.startswith('__') and attr.endswith('__'))
                and self.shell_globals.get(attr)
                ):

                self.shell_globals[attr] = getattr(module, attr)
                self._update_class_instances(module, attr)


    def _reload_models_module(self, app_name):
        """
        Reload Django models
        Based on http://stackoverflow.com/questions/890924/how-do-you-reload-a-django-model-module-using-the-interactive-interpreter-via-m
        """
        curdir = os.getcwd()
        cache = AppCache()
        for app in cache.get_apps():

            f = app.__file__
            if f.startswith(curdir) and f.endswith('.pyc'):
                try:
                    os.remove(f)
                except Exception:
                    pass
            __import__(app.__name__)
            reload(app)

        cache.app_store = SortedDict()
        cache.app_models = SortedDict()
        cache.app_errors = {}
        cache.handled = {}
        cache.loaded = False

        # Reset app's models in global scope
        # Using a dictionary here instead of cache.get_models(app_name)
        # The latter does not seem to work (look into that)
        reimported_app = importlib.import_module("{}.models".format(app_name))
        model_names = self.model_globals[app_name]
        for model_name in model_names:
            self.shell_globals[model_name] = getattr(reimported_app, model_name)
            self._update_class_instances(reimported_app, model_name)

    def _update_class_instances(self, module, attr):
        """
        Reset the __class__ of all instances whoses
        class has been reloaded into the shell

        This allows us to do CRAZY things such as
        effectively manipulate an instance's source code
        while inside a debugger
        """
        module_obj = getattr(module, attr)
        if inspect.isclass(module_obj):
            for obj in self.shell_globals.values():
                # hasattr condition attempts to handle old style classes
                # The class __str__ check may not be ideal but it seems to work
                # The one exception being if you changes the __str__ method
                # of the reloaded object.  That edge case is not handled
                if hasattr(obj, '__class__') and str(obj.__class__) == str(module_obj):
                    obj.__class__ = module_obj