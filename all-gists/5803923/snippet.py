from django.conf import settings
from django.core.files.storage import Storage
from django.utils import importlib


def load_class(class_string):
    class_module, class_name = class_string.rsplit('.', 1)
    class_module = importlib.import_module(class_module)
    return getattr(class_module, class_name)


class HybridStorage(Storage):
    """
    Allows you to declare a list of storage backends to use. For each operation,
    each is accessed in sequence until one returns successfully.

    The main use case is to allow us to develop with production imagery from S3,
    but to transparently handle any file uploads with local file storage (so as
    not to impact upon the production environment)
    """

    def __init__(self, backends=None):
        if not backends:
            backends = settings.HYBRID_STORAGE_BACKENDS
        self.backends = []

        for backend in backends:
            if isinstance(backend, Storage):
                self.backends.append(backend)
            elif isinstance(backend, basestring):
                self.backends.append(load_class(backend)())

    def _open(self, name, mode='rb'):
        for backend in self.backends:
            try:
                f = backend._open(name, mode=mode)
                return f
            except IOError:
                continue
        raise IOError('File does not exist: %s' % name)

    def _save(self, name, content):
        for backend in self.backends:
            try:
                result = backend._save(name, content)
                return result
            except IOError:
                continue
        raise IOError('Could not save file in any available backend')

    def _backend_for_name(self, name):
        for backend in self.backends:
            if backend.exists(name):
                return backend
            continue
        return None

    def delete(self, name):
        pass

    def exists(self, name):
        for backend in self.backends:
            if backend.exists(name):
                return True
            continue
        return False

    def listdir(self, path):
        """
        Collect the results of `listdir` on all backends, and then deduplicate
        """
        collected_directories = []
        collected_files = []
        for backend in self.backends:
            try:
                directories, files = backend.listdir(path)
                collected_directories.extend(directories)
                collected_files.extend(files)
            except:
                pass
        collected_directories = list(set(collected_directories))
        collected_files = list(set(collected_files))

        return collected_directories, collected_files

    def size(self, name):
        backend = self._backend_for_name(name)
        if backend:
            return backend.size(name)
        return None

    def url(self, name):
        backend = self._backend_for_name(name)
        if backend:
            return backend.url(name)
        return None

    def accessed_time(self, name):
        backend = self._backend_for_name(name)
        if backend:
            return backend.accessed_time(name)
        return None

    def created_time(self, name):
        backend = self._backend_for_name(name)
        if backend:
            return backend.created_time(name)
        return None

    def modified_time(self, name):
        backend = self._backend_for_name(name)
        if backend:
            return backend.modified_time(name)
        return None
