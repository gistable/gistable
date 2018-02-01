from tastypie.fields import ListField

class TaggedResource(ModelResource):
    tags = ListField()
    
    class Meta:
        queryset = Model.objects.all()

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}

        orm_filters = super(TaggedResource, self).build_filters(filters)

        if 'tag' in filters:
            orm_filters['tags__name__in'] = filters['tag'].split(',')
        return orm_filters

        
    def dehydrate_tags(self, bundle):
        return map(str, bundle.obj.tags.all())


    def save_m2m(self, bundle):
        tags = bundle.data.get('tags', [])
        bundle.obj.tags.set(*tags)
        return super(TaggedResource, self).save_m2m(bundle)

