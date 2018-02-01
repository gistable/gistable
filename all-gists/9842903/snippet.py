from django.views.generic import TemplateView


if settings.DEBUG:

    # enable local preview of error pages
    urlpatterns += patterns('',
        (r'^403/$', TemplateView.as_view(template_name="403.html")),
        (r'^404/$', TemplateView.as_view(template_name="404.html")),
        (r'^500/$', TemplateView.as_view(template_name="500.html")),
    )