from django.conf.urls import patterns, url, include
from rest_framework_mongoengine.routers import MongoSimpleRouter
from api.views import TodoViewSet


router = MongoSimpleRouter()
router.register(r'todo', TodoViewSet)

urlpatterns = patterns(
    '',
    url(r'^', include(router.urls)),
)