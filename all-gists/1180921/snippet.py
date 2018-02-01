# source of a massive memory leak in a Django app (if obj is QuerySet):
if not obj:
    return None