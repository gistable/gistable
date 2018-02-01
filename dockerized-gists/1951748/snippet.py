def update(instance, **kwargs):
    """Helper to update instance of the model with data from kwargs."""
    instance.__class__.objects.filter(pk=instance.pk).update(**kwargs)
