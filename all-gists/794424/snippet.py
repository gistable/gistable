from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.bundle import Bundle
from tastypie.exceptions import NotFound
from tastypie.resources import Resource


# a dummy class representing a row of data
class Row(object):
    id = None
    name = ''


# create some rows
r1 = Row()
r1.id = 1
r1.name = 'foo'

r2 = Row()
r2.id = 2
r2.name = 'bar'

r3 = Row()
r3.id = 3
r3.name = 'baz'

# data dictionary... a real bare-bones data source
data = { 1: r1, 2: r1, 3: r3 }


class RowResource(Resource):
    # fields must map to the attributes in the Row class
    id = fields.IntegerField(attribute = 'id')
    name = fields.CharField(attribute = 'name')
    
    class Meta:
        resource_name = 'row'
        object_class = Row
        authentication = Authentication()
        authorization = Authorization()

    # adapted this from ModelResource
    def get_resource_uri(self, bundle_or_obj):
        kwargs = {
            'resource_name': self._meta.resource_name,
        }

        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.id # pk is referenced in ModelResource
        else:
            kwargs['pk'] = bundle_or_obj.id
        
        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name
        
        return self._build_reverse_url('api_dispatch_detail', kwargs = kwargs)

    def get_object_list(self, request):
        # inner get of object list... this is where you'll need to
        # fetch the data from what ever data source
        return data.values()

    def obj_get_list(self, request = None, **kwargs):
        # outer get of object list... this calls get_object_list and
        # could be a point at which additional filtering may be applied
        return self.get_object_list(request)

    def obj_get(self, request = None, **kwargs):
        # get one object from data source
        pk = int(kwargs['pk'])
        try:
            return data[pk]
        except KeyError:
            raise NotFound("Object not found") 
    
    def obj_create(self, bundle, request = None, **kwargs):
        # create a new row
        bundle.obj = Row()
        
        # full_hydrate does the heavy lifting mapping the
        # POST-ed payload key/values to object attribute/values
        bundle = self.full_hydrate(bundle)
        
        # we add it to our in-memory data dict for fun
        data[bundle.obj.id] = bundle.obj
        return bundle
    
    def obj_update(self, bundle, request = None, **kwargs):
        # update an existing row
        pk = int(kwargs['pk'])
        try:
            bundle.obj = data[pk]
        except KeyError:
            raise NotFound("Object not found")
        
        # let full_hydrate do its work
        bundle = self.full_hydrate(bundle)
        
        # update existing row in data dict
        data[pk] = bundle.obj
        return bundle
