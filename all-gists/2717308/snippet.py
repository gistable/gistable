# models.py
class Link(models.Model):                                                       
    .....
    place = models.ManyToManyField("PlaceForLink", through="LinkPlace", related_name="link")
    .....          
    place.hasplace_filter = True

# filters.py
class HasPlaceFilterSpec(FilterSpec):                                           
    def __init__(self, f, request, params, model, model_admin, field_path=None):
        super(HasPlaceFilterSpec, self).__init__(                               
            f, request, params, model, model_admin, field_path=field_path)      
        self.lookup_val = request.GET.get('has_place', None)                    
                                                                                
    def choices(self, cl):                                                      
        yield {'selected': self.lookup_val is None,                             
               'query_string': cl.get_query_string({}, ['has_place']),          
               'display': _('All')}                                             
        for pk_val, val in (('yes', _('Yes')), ('no', _('No'))):                
            yield {'selected': self.lookup_val == pk_val,                       
                   'query_string': cl.get_query_string({'has_place' : pk_val}), 
                   'display': val}                                              
                                                                                
    def filter(self, params, qs):                                               
        if 'has_place' in params:                                               
            if params['has_place'] == 'no':                                     
                qs = qs.exclude(place__id__gt=0)                                
            else:                                                               
                qs = qs.filter(place__id__gt=0)                                 
            del params['has_place']                                             
        return qs                                                               
                                                                                
    def title(self):                                                            
        # return the title displayed above your filter                          
        return _('Has place')                                                   
                                                                                
# Here, we insert the new FilterSpec at the first position, to be sure          
# it gets picked up before any other                                            
FilterSpec.filter_specs.insert(0,                                               
  # If the field has a `hasplace_filter` attribute set to True                  
  # the this FilterSpec will be used                                            
  (lambda f: getattr(f, 'hasplace_filter', False), HasPlaceFilterSpec)          
)

# admin.py

# Defining my own change list for link
# adding `filter` method for overwriting default queryset
class CustomFilterSpecChangeList(ChangeList):

    # Here we are doing our own initialization so the filters
    # are initialized when we request the data
    def __init__(self, request, model, list_display, list_display_links, list_filter, date_hierarchy, search_fields, list_select_related, list_per_page, list_editable, model_admin):
        self.model = model
        self.opts = model._meta
        self.lookup_opts = self.opts
        self.root_query_set = model_admin.queryset(request)
        self.list_display = list_display
        self.list_display_links = list_display_links
        self.list_filter = list_filter
        self.date_hierarchy = date_hierarchy
        self.search_fields = search_fields
        self.list_select_related = list_select_related
        self.list_per_page = list_per_page
        self.model_admin = model_admin

        # Get search parameters from the query string.
        try:
            self.page_num = int(request.GET.get(PAGE_VAR, 0))
        except ValueError:
            self.page_num = 0
        self.show_all = ALL_VAR in request.GET
        self.is_popup = IS_POPUP_VAR in request.GET
        self.to_field = request.GET.get(TO_FIELD_VAR)
        self.params = dict(request.GET.items())
        if PAGE_VAR in self.params:
            del self.params[PAGE_VAR]
        if TO_FIELD_VAR in self.params:
            del self.params[TO_FIELD_VAR]
        if ERROR_FLAG in self.params:
            del self.params[ERROR_FLAG]

        if self.is_popup:
            self.list_editable = ()
        else:
            self.list_editable = list_editable
        self.order_field, self.order_type = self.get_ordering()
        self.query = request.GET.get(SEARCH_VAR, '')
        # Get filter_specs before get_query_set is called cause we need them there
        self.filter_specs, self.has_filters = self.get_filters(request)
        self.query_set = self.get_query_set()
        self.get_results(request)
        self.title = (self.is_popup and ugettext('Select %s') % force_unicode(self.opts.verbose_name) or ugettext('Select %s to change') % force_unicode(self.opts.verbose_name))
        self.pk_attname = self.lookup_opts.pk.attname


    # To be able to do our own filter,
    # we need to override this
    def get_query_set(self):

        qs = self.root_query_set
        params = self.params.copy()

        # now we pass the parameters and the query set 
        # to each filter spec that may change it
        # The filter MUST delete a parameter that it uses
        if self.has_filters: 
            for filter_spec in self.filter_specs:
                if hasattr(filter_spec, 'filter'):
                    qs = filter_spec.filter(params, qs)

        # Now we call the parent get_query_set()
        # method to apply subsequent filters
        sav_qs = self.root_query_set
        sav_params = self.params

        self.root_query_set = qs
        self.params = params

        qs = super(CustomFilterSpecChangeList, self).get_query_set()

        self.root_query_set = sav_qs
        self.params = sav_params

        return qs

class LinkAdmin(admin.ModelAdmin):
    ...
    list_filter = ('place',)
    ...

    def get_changelist(self, request, **kwargs):
        """ Overriden from ModelAdmin """
        return CustomFilterSpecChangeList