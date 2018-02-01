import colander as c
import deform.widget as w
from deform.form import Form
from deform.schema import FileData
import os

here = os.path.dirname(__file__)

class Store(dict):
    def preview_url(self, name):
        return ""

store = Store()

class SampleSchema(c.MappingSchema):
    name = c.SchemaNode(c.String())
    image = c.SchemaNode(FileData(), widget=w.FileUploadWidget(store))

@view_config(route_name='home', renderer='templates/mytemplate.pt', request_method="GET")
def my_view(request):
    form = Form(SampleSchema(), buttons=('up',))
    return {'project':'fileupload', 'form': form}

@view_config(route_name='home', renderer='templates/mytemplate.pt', request_method="POST")
def my_post(request):
    form = Form(SampleSchema(), buttons=('up',))
    controls = request.params.items()
    params = form.validate(controls)
    f = params['image']
    request.response.body = f['fp'].read()
    f['fp'].close()
    return request.response
