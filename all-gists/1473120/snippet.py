from django.views.generic import View
from django.utils import simplejson


class JSONResponseView(View):

    def render_to_response(self, data, **httpresponse_kwargs):
        "Retuns a json response based on the context"
        json_data = simplejson.dumps(data)
        return HttpResponse(json_data, content_type="application/json", **httpresponse_kwargs)