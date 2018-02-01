#!/usr/bin/python
# coding: utf-8

import json


class JSONResponseMixin(object):
    """
    A mixin that can be used to render a JSON response.
    """

    def dateHandler(self, obj):
        return obj.isoformat() if hasattr(obj, 'isoformat') else obj

    def convertToJson(self, response):
        return json.dumps(response, ensure_ascii=False,
                          default=self.dateHandler)

    def jsonResponse(self, response, **response_kwargs):
        response_kwargs['content_type'] = 'application/json'
        return self.response_class(self.convertToJson(response),
                                   **response_kwargs)