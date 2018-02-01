import sys, os.path, logging


try:
    import sysconfig
except ImportError:
    sysconfig = None

def warn_on_path_overlap():
    """
    Importing modules under multiple sys.modules names
      (e.g. borrow, apps.borrow)
    is a terrible python wart.  It causes many subtle bugs.

    This function will issue a logged error if it finds any modules
      with duplicate keys in sys.modules (based on matching paths).

    It takes a bit to run, but will save your sanity.

    It's only useful once duplicates are loaded, so make sure to
    exercise your imports before running.
    """
    ignored_paths = set() # Ignore stdlib paths
    if sysconfig is not None:
        for path_name in sysconfig.get_path_names():
            ignored_paths.add(sysconfig.get_path(path_name))

    def is_ignored_path(module_path):
        for path in ignored_paths:
            # FIXME: this excludes user packages in site-packages because it is a subdir of stdlib.
            # Fix that.
            if os.path.commonprefix([path, module_path]) == path:
                return True
        return False

    ignored_modules = set([ # Yes, the email stdlib packages really does alias all these.
        "email.Header","email.header","email.FeedParser","email.feedparser",
        "email.MIMEMessage","email.mime.message","email.MIMEBase",
        "email.mime.base","email.MIMEImage","email.mime.image",
        "email.MIMEText","email.mime.text","email.Message","email.message",
        "email.Errors","email.errors","email.MIMEMultipart","email.mime.multipart",
        "email.quopriMIME","email.quoprimime","email.MIMENonMultipart",
        "email.mime.nonmultipart","email.Parser","email.parser","email.Generator",
        "email.generator","email.MIMEAudio","email.mime.audio","email.Iterators",
        "email.iterators","email.base64MIME","email.base64mime","email.Charset",
        "email.charset","email.Utils","email.utils","email.Encoders","email.encoders"
    ])
    def is_ignored_module(module_key):
        return module_key in ignored_modules

    def get_module_path(module_key):
        module = sys.modules[module_key]
        if module is None:
            # Seems to happen on builtins...
            return None
        if not hasattr(module, '__file__'):
            # Happens on C modules
            return None
        return module.__file__

    seen_comparisons = set()
    for outer_key in sys.modules.keys():
        if is_ignored_module(outer_key):
            continue

        outer_path = get_module_path(outer_key)
        if outer_path is None:
            continue
        if is_ignored_path(outer_path):
            continue

        for inner_key in sys.modules.keys():
            if outer_key == inner_key: # Skip if the module is the very same.
                continue

            comparison = tuple(sorted([outer_key, inner_key])) # Avoid listing twice.
            if comparison in seen_comparisons:
                continue
            else:
                seen_comparisons.add(comparison)

            inner_path = get_module_path(inner_key)
            if inner_path is None:
                continue

            if inner_path == outer_path:
                logging.error("Differently-named modules have the same implementation: %s, %s; Fix your sys.path to not cause duplicate paths to packages, and avoid relative imports.", outer_key, inner_key)
