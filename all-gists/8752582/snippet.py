from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import admin

from application.views import ApplicationFormView, ApplicationListView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', login_required(ApplicationFormView.as_view())),
    url(r'^applist/', staff_member_required(ApplicationListView.as_view())),
    url(r'^admin/', include(admin.site.urls)),
)
