if not hasattr(ForeignModel, "tags"):
    t = TaggableManager()
    t.contribute_to_class(ForeignModel, "tags")