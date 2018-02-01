from django.contrib.syndication.views import Feed
from django.views.generic import View


class FeedView(View, Feed):

    def get(self, request, *args, **kwargs):
        return self(request, *args, **kwargs)