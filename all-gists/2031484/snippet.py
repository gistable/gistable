"""
Simple setup for tastypie with Solr as the backend.  This is based off Daniel Lindsley's Pycon 2012 presentation.  Minor modifications.  

http://speakerdeck.com/u/daniellindsley/p/restful-apis-with-tastypie

http://django-tastypie.readthedocs.org/

"""

import pysolr
from tastypie import fields
from tastypie.resources import Resource

class SolrObject(object):
    def __init__(self, initial=None):
        self.__dict__['_data'] = initial or {}
    def __getattr__(self, key):
        return self._data.get(key, None)
    def to_dict(self):
        return self._data

class SolrResource(Resource):
    id = fields.CharField(attribute='id', default='id')
    title = fields.CharField(attribute='title', default='title')
    discipline = fields.ListField(attribute='discipline', default=[])
    author = fields.CharField(attribute='call_number', null=True, blank=True)
    
    
    class Meta:
        resource_name = 'solr'
        object_class = SolrObject
        app_base = 'http://yourdomain.net/object/%s'
    
    def get_resource_uri(self, bundle_or_obj):
        return self._meta.app_base % bundle_or_obj.obj.id
    
    def get_object_list(self, request, **kwargs):
        query = kwargs.get('query', None) or request.GET.get('q', '*:*')
        
        solr = pysolr.Solr('http://localhost:8983/solr/')
        
        sset = [SolrObject(initial=res) for res in solr.search(query)]
        return sset
    
    def obj_get_list(self, request=None, **kwargs):
        query = request.GET.get('query', None)
        if query:
            self._meta.query = query
        return self.get_object_list(request, query=query)
    
    def obj_get(self, request=None, **kwargs):
        return self.get_object_list(request, query='id:%s' % kwargs['pk'])[0]
    