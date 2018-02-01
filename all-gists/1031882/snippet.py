# ...

class Category(Base):
    
    slug = models.SlugField(_(u'slug'), max_length=100, unique=True)
    title = models.CharField(_(u'title'), max_length=250)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='child')
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['title']
    
    def __unicode__(self):
        p_list = self._recurse_for_parents(self)
        p_list.append(self.title)
        return self.get_separator().join(p_list)
    
    def _recurse_for_parents(self, cat_obj):
        p_list = []
        if cat_obj.parent_id:
            p = cat_obj.parent
            p_list.append(p.title)
            more = self._recurse_for_parents(p)
            p_list.extend(more)
        if cat_obj == self and p_list:
            p_list.reverse()
        return p_list
    
    def get_separator(self):
        return ' :: '
    
    def _parents_repr(self):
        p_list = self._recurse_for_parents(self)
        return self.get_separator().join(p_list)
    _parents_repr.short_description = 'Category parents'
    
    def save(self):
        p_list = self._recurse_for_parents(self)
        if self.title in p_list:
            raise validators.ValidationError('You must not save a category in itself')
        super(Category, self).save()
    
    @models.permalink
    def get_absolute_url(self):
        return ('category_index', (), { 'category': self.slug })