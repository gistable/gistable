#
# by default, django 404 and 500 pages dont pass context to templates.
# as you almost *always* need context variables in your custom 
# 404/500 templates, you might need MEDIA_URL for example
#
# you need to create a custom view for errors and register it in your urls.py
#
# in urls.py add :
#
# handler500 = handler404 = views.server_error
#
#

def server_error(request, template_name='500.html'):
    from django.template import RequestContext
    from django.http import HttpResponseServerError
    t = get_template(template_name)
    return HttpResponseServerError(t.render(RequestContext(request)))