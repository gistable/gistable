from sandbox import models
from tastypie import fields
from apibase.resources import CamayakModelResource
from django.conf.urls.defaults import url

class ModelResource(CamayakModelResource):
    def override_urls(self):
        urls = []
    
        for name, field in self.fields.items():
            if isinstance(field, fields.ToManyField):
                print field.to_class
                resource = r"^(?P<resource_name>{resource_name})/(?P<{related_name}>.+)/{related_resource}/$".format(
                    resource_name=self._meta.resource_name, 
                    related_name=field.related_name,
                    related_resource=field.attribute,
                    )
                resource = url(resource, field.to_class().wrap_view('get_list'), name="api_dispatch_detail")
                urls.append(resource)
        return urls

class HandResource(ModelResource):
    fingers = fields.ToManyField('sandbox.api.FingerResource', 'fingers', 'hand')

    class Meta:
        queryset = models.Hand.objects.all()
        resource_name = 'hands'
        api_name = 'v1'

class FingerResource(ModelResource):
    hand = fields.ForeignKey('sandbox.api.HandResource', 'hand')
    bones = fields.ToManyField('sandbox.api.BoneResource', 'bones', 'finger')

    class Meta:
        queryset = models.Finger.objects.all()
        resource_name = 'fingers'
        api_name = 'v1'

        filtering = {
            "hand": ('exact',),
            }

class BoneResource(ModelResource):
    finger = fields.ForeignKey('sandbox.api.BoneResource', 'finger')
    
    class Meta:
        queryset = models.Bone.objects.all()
        resource_name = 'bones'
        api_name = 'v1'

        filtering = {
            "finger": ('exact',),
            }