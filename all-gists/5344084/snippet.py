"""
The following mixins and views are borrowed and adapted from the following
gist:
            https://gist.github.com/michelts/1029336
"""
from functools import partial

from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import ProcessFormView, FormMixin


class MultipleFormsMixin(FormMixin):
    """
    A mixin that provides a way to show and handle several forms in a
    request. Forms are provided in the class attribute *form_classes* which
    provides a mapping of form names to form classes. The form name is used
    as identifier and automatically put into the context when calling
    ``get_context_data``.
    Providing keyword arguments for the forms uses ``get_form_kwargs`` by
    default for every form class. For convenience, adding specific keywords
    to an individiual form is also possible by calling the
    ``get_<form_key>_kwargs``, e.g. for a form class with key *basket_form*,
    you would call ``get_basket_form_kwargs``.
    It is also easy to get an individual form instance by calling either
    ``get_form`` with the *key* as argument or the corresponding
    ``get_basket_form()`` method for convenience. To prevent instantiating
    the forms multiple times throughout the request cycle, the form instances
    are cached on the instance. If ``get_form`` is called and the instance
    are not populated, yet, all forms are instantiated and cached before
    returning the requested form instance.
    """
    form_classes = {} # set the form classes as a mapping
    # we are caching instatiated forms here to make sure that we can get
    # individual instances from forms easier and don't have to worry about
    # instantiating them multiple times through out the course of a
    # request cycle.
    _cached_forms = {}

    def get_form_classes(self):
        return self.form_classes

    def get_forms(self, form_classes):
        if self._cached_forms:
            return self._cached_forms
        self._cached_forms = {}
        for key, form_class in form_classes.items():
            kwargs = getattr(self, 'get_{0}_kwargs'.format(key),
                             self.get_form_kwargs)()
            self._cached_forms[key] = form_class(**kwargs)
        return self._cached_forms

    def __getattr__(self, name):
        form_key = name.replace('get_', '')
        if form_key in self.form_classes:
            return partial(self.get_form, form_key)
        return super(MultipleFormsMixin, self).__getattr__(name)

    def get_form(self, key):
        if not self._cached_forms:
            self.get_forms(self.form_classes)
        return self._cached_forms[key]

    def get_context_data(self, **kwargs):
        kwargs = super(MultipleFormsMixin, self).get_context_data(**kwargs)
        kwargs.update(self._cached_forms)
        return kwargs

    def forms_valid(self, forms):
        return super(MultipleFormsMixin, self).form_valid(forms)

    def forms_invalid(self, forms):
        return self.render_to_response(self.get_context_data(forms=forms))


class ProcessMultipleFormsView(ProcessFormView):
    """
    A mixin that processes multiple forms on POST. Every form must be
    valid.
    """
    validation_results = {}

    def validate_forms(self, forms):
        """
        Validate forms against each other in here. This should return a
        dictionary of validation result with *form_key* and validation result.
        """
        return {}

    def is_form_valid(self, form_key):
        """
        Get the validation result for the given *form_key*. This requires the
        validation to be run previously.
        """
        return self.validation_results.get(form_key)

    def check_forms_are_valid(self, forms):
        self.validation_results = {}
        for form_key, form in forms.items():
            self.validation_results[form_key] = form.is_valid()
        # allow for cross-form validation and update the validation resuts
        self.validation_results.update(self.validate_forms(forms))
        return all(self.validation_results.values())

    def get(self, request, *args, **kwargs):
        form_classes = self.get_form_classes()
        forms = self.get_forms(form_classes)
        return self.render_to_response(self.get_context_data(forms=forms))

    def post(self, request, *args, **kwargs):
        form_classes = self.get_form_classes()
        forms = self.get_forms(form_classes)
        if self.check_forms_are_valid(forms):
            return self.forms_valid(forms)
        else:
            return self.forms_invalid(forms)


class BaseMultipleFormsView(MultipleFormsMixin, ProcessMultipleFormsView):
    """
    A base view for displaying several forms.
    """

class MultipleFormsView(TemplateResponseMixin, BaseMultipleFormsView):
    """
    A view for displaing several forms, and rendering a template response.
    """
