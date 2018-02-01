    def post_list(self, request, **kwargs):
       deserialized = self.deserialize(request,
                                       request.raw_post_data,
                                       format=request.META.get('CONTENT_TYPE',
                                                               'application/json'))
       bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized))
       self.is_valid(bundle, request)
       updated_bundle = self.obj_create(bundle, request=request)
       resp = self.create_response(request,
                                   self.full_dehydrate(updated_bundle.obj))
       resp["location"] = self.get_resource_uri(updated_bundle)
       resp.code = 201
       return resp
                          