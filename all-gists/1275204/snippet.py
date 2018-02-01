#views.py

from django.views.generic import UpdateView

class UpdateBook(UpdateView):

    model = Book
    form_class = BookForm
    template_name = 'create_form.html'
    success_url = '/books/'


#urls.py

from django.conf.urls import *
from library.views import UpdateBook

urlpatterns = patterns('',
    url('^update_book/(?P<pk>[\w-]+)$', UpdateBook.as_view(), name='update_book'),
)
# you MUST pass a pk or slug param to this view
