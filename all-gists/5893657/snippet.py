
class OrganCreateView(PagedPerviousMixin, CreateView):
    model = Organ
    form_class = OrganForm

    template_name = 'shared/admin/organ_form.html'

    def get_context_data(self, **kwargs):
        context = super(OrganCreateView, self).get_context_data(**kwargs)
        if self.request.method == 'POST':
            context['formset'] = OrganContactFormset(self.request.POST)
        else:
            context['formset'] = OrganContactFormset()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            instance = form.save()
            formset.instance = instance
            formset.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super(OrganCreateView, self).form_valid(form)


class OrganUpdateView(PagedPerviousMixin, UpdateView):
    model = Organ
    form_class = OrganForm
    template_name = 'shared/admin/organ_form.html'

    def get_context_data(self, **kwargs):
        context = super(OrganUpdateView, self).get_context_data(**kwargs)
        if self.request.method == 'POST':
            context['formset'] = OrganContactFormset(self.request.POST, instance=self.object)
        else:
            context['formset'] = OrganContactFormset(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            form.save()
            formset.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super(OrganUpdateView, self).form_valid(form)