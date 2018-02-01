from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _

from youproject.yourapp import views


people_list = login_required(views.PeopleListView.as_view())
people_detail = login_required(views.PeopleDetailView.as_view())


urlpatterns = patterns(
    '',
    url(_(r'^$'), people_list, name="people_list"),
    url(_(r'^(?P<pk>\d+)/$'), people_detail, name="people_detail"),
)
