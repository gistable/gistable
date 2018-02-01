class FieldSelectMixin(object):
    """
    Mixin to allow field selection.
    This has to be done in two parts:
    1) In model queryset for database selection. This need to be in some code section
    where the queryset is ready, but still not evaluated. obj_get_list and obj_get are perfect
    for Tastypie GET requests.
    2) In full_dehydrate method, to prevent from Tastypie fetching all the fields from the model.
    """
    def full_dehydrate(self, bundle, for_list=False):
        """
        Given a bundle with an object instance, extract the information from it
        to populate the resource.
        """
        use_in = ['all', 'list' if for_list else 'detail']
 
        field_list = self.fields.items()

        # Get values if fields is set in query
        if hasattr(bundle.request, 'GET'):
            selectedFields = bundle.request.GET.get('fields')
            # If selectedFields has data turn it into a list
            if selectedFields:
                selectedFields = selectedFields.split(',')
                # Iterate only on the selected fields
                field_list = [(f_n, f_o) for f_n, f_o in field_list if f_n in selectedFields]

        # Dehydrate each field.
        for field_name, field_object in field_list:
            # If it's not for use in this mode, skip
            field_use_in = getattr(field_object, 'use_in', 'all')
            if callable(field_use_in):
                if not field_use_in(bundle):
                    continue
            else:
                if field_use_in not in use_in:
                    continue
 
            # A touch leaky but it makes URI resolution work.
            if getattr(field_object, 'dehydrated_type', None) == 'related':
                field_object.api_name = self._meta.api_name
                field_object.resource_name = self._meta.resource_name
 
            bundle.data[field_name] = field_object.dehydrate(bundle, for_list=for_list)
 
            # Check for an optional method to do further dehydration.
            method = getattr(self, "dehydrate_%s" % field_name, None)
 
            if method:
                bundle.data[field_name] = method(bundle)
 
        bundle = self.dehydrate(bundle)
        return bundle

    def select_fields(self, bundle, queryset):
        """
        Given an optional field list in GET query, tells the model queryset
        to only select a list of fields from db.
        """
        if hasattr(bundle.request, 'GET'):
            selectedFields = bundle.request.GET.get('fields')
            # If selectedFields has data turn it into a list
            if selectedFields:
                selectedFields = selectedFields.split(',')
                # only() to select only the requested fields
                # select_related() to generate SQL joins on OneToMany relations and call just one query
                # Django will take care of incorrect args (i.e. passing a non-relation field to select_related())
                queryset = queryset.select_related(*selectedFields).only(*selectedFields)
        return queryset

    def obj_get_list(self, bundle, **kwargs):
        """
        A ORM-specific implementation of ``obj_get_list``.
        Takes an optional ``request`` object, whose ``GET`` dictionary can be
        used to narrow the query.
        """
        filters = {}

        if hasattr(bundle.request, 'GET'):
            # Grab a mutable copy.
            filters = bundle.request.GET.copy()

        # Update with the provided kwargs.
        filters.update(kwargs)
        applicable_filters = self.build_filters(filters=filters)

        try:
            objects = self.select_fields(bundle, self.apply_filters(bundle.request, applicable_filters))
            return self.authorized_read_list(objects, bundle)
        except ValueError:
            raise BadRequest("Invalid resource lookup data provided (mismatched type).")

    def obj_get(self, bundle, **kwargs):
        """
        A ORM-specific implementation of ``obj_get``.
        Takes optional ``kwargs``, which are used to narrow the query to find
        the instance.
        """
        try:
            object_list = self.select_fields(bundle, self.get_object_list(bundle.request).filter(**kwargs))
            stringified_kwargs = ', '.join(["%s=%s" % (k, v) for k, v in kwargs.items()])

            if len(object_list) <= 0:
                raise self._meta.object_class.DoesNotExist("Couldn't find an instance of '%s' which matched '%s'." % (self._meta.object_class.__name__, stringified_kwargs))
            elif len(object_list) > 1:
                raise MultipleObjectsReturned("More than '%s' matched '%s'." % (self._meta.object_class.__name__, stringified_kwargs))

            bundle.obj = object_list[0]
            self.authorized_read_detail(object_list, bundle)
            return bundle.obj
        except ValueError:
            raise NotFound("Invalid resource lookup data provided (mismatched type).")
