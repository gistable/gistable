"""
This generic view displays a list of objects and a simple ModelForm to add a new
object to the list.
Just subclass this view and override the attributes and methods that you need. You
will probably need to override at least 'model', 'form_class' and 'success_url'.
See the documentation of the used mixins and ProcessFormView in
https://docs.djangoproject.com/en/1.4/ref/class-based-views/
"""
from django.views.generic.list import MultipleObjectMixin, MultipleObjectTemplateResponseMixin
from django.views.generic.edit import ModelFormMixin, ProcessFormView

class ListAppendView(MultipleObjectMixin,
        MultipleObjectTemplateResponseMixin,
        ModelFormMixin,
        ProcessFormView):
    """ A View that displays a list of objects and a form to create a new object.
    The View processes this form. """
    template_name_suffix = '_append'
    allow_empty = True

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()
        if not allow_empty and len(self.object_list) == 0:
            raise Http404(_(u"Empty list and '%(class_name)s.allow_empty' is False.")
                          % {'class_name': self.__class__.__name__})
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = self.get_context_data(object_list=self.object_list, form=form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = None
        return super(ListAppendView, self).post(request, *args, **kwargs)

    def form_invalid(self, form):
        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data(object_list=self.object_list, form=form))

