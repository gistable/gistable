class MyInline(admin.TabularInline):
    model = MyModel
    extra = 0
    template = 'admin/edit_inline/list.html'

    def get_formset(self, request, obj=None, **kwargs):
        FormSet = super(ActivationKeyInline, self).get_formset(request, obj, **kwargs)
        class NewFormSet(FormSet):
            def _construct_forms(self, *args, **kwargs):
                qs = self.get_queryset()
                
                paginator = Paginator(qs, 20)
        
                try:
                    page_num = int(request.GET.get('page', '1'))
                except ValueError:
                    page_num = 1
                    
                try:
                    page = paginator.page(page_num)
                except (EmptyPage, InvalidPage):
                    page = paginator.page(paginator.num_pages)
                
                self.paginator = paginator
                self.page = page
                self._queryset = page.object_list
                self.max_num = len(page.object_list)
                
                return super(NewFormSet, self)._construct_forms(*args, **kwargs)
        return NewFormSet