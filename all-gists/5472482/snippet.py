# admin.py: admin action definition
def make_copy(self, request, queryset):
    form = None

    if 'apply' in request.POST:
        form = CopyPageForm(request.POST)

        if form.is_valid():
            issue = form.cleaned_data['issue']

            for page in queryset:
                new_page = Pages()
                new_page.no = page.no
                new_page.issue = issue
                new_page.save()

            self.message_user(request, _("%s %s." % (ugettext('Selected pages copied to issue'), issue)))

            return HttpResponseRedirect(request.get_full_path())

    if not form:
        form = CopyPageForm(initial={'_selected_action': request.POST.getlist(ACTION_CHECKBOX_NAME)})

    opts = self.model._meta
    app_label = opts.app_label

    return render_to_response(
        'admin/pages/copy_form.html',
        {'pages': queryset, 'copy_form': form, "opts": opts, "app_label": app_label},
        context_instance=template.RequestContext(request)
    )

make_copy.short_description = _(u'copy to issue')

# forms.py: intermediate page form
from django import forms
from django.utils.translation import ugettext_lazy as _

from mobileissue.models import Issue


class CopyPageForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    issue = forms.ModelChoiceField(Issue.objects, label=_('Name'))

# copy_form.html: intermediate page template
{% extends "admin/base_site.html" %}
{% load i18n l10n %}
{% load url from future %}
{% load admin_urls %}

{% block breadcrumbs %}
    <div class="breadcrumbs">
        <a href="{% url 'admin:index' %}">{% trans 'Home' %}</a>
        &rsaquo; <a href="{% url 'admin:app_list' app_label=app_label %}">{{ app_label|capfirst|escape }}</a>
        &rsaquo; <a href="{% url opts|admin_urlname:'changelist' %}">{{ opts.verbose_name_plural|capfirst }}</a>
        &rsaquo; {% trans 'Copy selected pages' %}
    </div>
{% endblock %}

{% block content %}

<p>{% trans 'Select issue' %}:</p>

<form action="" method="post">
    {% csrf_token %}

    {{ copy_form }}

    <p>{% trans 'Pages to copy' %}:</p>

    <ul>
        {% for page in pages %}
            <li>{{ page.no }} - {{ page.issue.name }}</li>
        {% endfor %}
    </ul>

    <input type="hidden" name="action" value="make_copy" />
    <input type="submit" name="apply" value="{% trans 'Copy' %}" />
</form>

{% endblock %}
