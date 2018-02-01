# urls.py
urlpatterns = patterns('',
    # ...

    # Example for custom view
    url(r'^admin/custom/$', views.custom_view),

    # ...

    # Admin
    url(r'^admin/', include(admin.site.urls)),
)

# views.py
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response
from django.template import RequestContext

@staff_member_required
def custom_view(request):
    context = {
        'title': 'Custom view',
    }

    template = 'admin/custom_view.html'
    return render_to_response(template, context,
                              context_instance=RequestContext(request))
