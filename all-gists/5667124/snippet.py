        def non_signal_save(obj, **kwargs):
            obj.__class__.objects.filter(pk=obj.pk).update(**kwargs)

# e.g. non_signal_save(blogpost, modified=hour_ago)