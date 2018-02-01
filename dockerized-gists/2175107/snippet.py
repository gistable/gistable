import os


def walk(storage, top='/', topdown=False, onerror=None):
    """An implementation of os.walk() which uses the Django storage for
    listing directories."""
    try:
        dirs, nondirs = storage.listdir(top)
    except os.error, err:
        if onerror is not None:
            onerror(err)
        return

    if topdown:
        yield top, dirs, nondirs
    for name in dirs:
        new_path = os.path.join(top, name)
        for x in walk(storage, new_path):
            yield x
    if not topdown:
        yield top, dirs, nondirs