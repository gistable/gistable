class ForwardInlineModelForm(InlineModelFormField):

    def __init__(self, form, session, model, prop, inline_view, **kwargs):
        """
            Default constructor.

            :param form:
                Form for the related model
            :param session:
                SQLAlchemy session
            :param model:
                Related model
            :param prop:
                Related property name
            :param inline_view:
                Inline view
        """
        self.form = form
        self.session = session
        self.model = model
        self.prop = prop
        self.inline_view = inline_view

        self._pk = get_primary_key(model)

        # Generate inline form field
        form_opts = FormOpts(widget_args=getattr(inline_view, 'form_widget_args', None),
                             form_rules=inline_view._form_rules)

        super().__init__(form, self._pk, form_opts=form_opts, **kwargs)

    def populate_obj(self, obj, name):
        value = getattr(obj, name, None)
        inline_form = self.form

        if value:
            model = value
        else:
            model = self.model()
            setattr(obj, name, model)

        for name, field in iteritems(self.form._fields):
            if name != self._pk:
                field.populate_obj(model, name)
        self.inline_view.on_model_change(inline_form, model)


class ForwardInlineModelConverter(InlineModelConverter):

    inline_field_list_type = ForwardInlineModelForm

    def contribute(self, model, form_class, inline_model):
        mapper = model._sa_class_manager.mapper
        info = self.get_info(inline_model)

        # Find property from target model to current model
        target_mapper = info.model._sa_class_manager.mapper

        forward_prop = None

        for prop in mapper.iterate_properties:
            if hasattr(prop, 'direction') and prop.direction.name == 'MANYTOONE':
                if prop.mapper.class_ == target_mapper.class_:
                    forward_prop = prop
                    break
        else:
            raise Exception('Cannot find forward relation for model %s' % info.model)

        reverse_prop = None

        for prop in target_mapper.iterate_properties:
            if hasattr(prop, 'direction') and prop.direction.name == 'ONETOMANY':
                if prop.mapper.class_ == mapper.class_:
                    reverse_prop = prop
                    break
        else:
            raise Exception('Cannot find reverse relation for model %s' % info.model)

        # Remove reverse property from the list
        ignore = [reverse_prop.key]

        if info.form_excluded_columns:
            exclude = ignore + list(info.form_excluded_columns)
        else:
            exclude = ignore

        # Create converter
        converter = self.model_converter(self.session, info)

        # Create form
        child_form = info.get_form()

        if child_form is None:
            child_form = get_form(info.model,
                                  converter,
                                  only=info.form_columns,
                                  exclude=exclude,
                                  field_args=info.form_args,
                                  hidden_pk=True)

        # Post-process form
        child_form = info.postprocess_form(child_form)

        kwargs = dict()

        label = self.get_label(info, forward_prop.key)
        if label:
            kwargs['label'] = label

        if self.view.form_args:
            field_args = self.view.form_args.get(forward_prop.key, {})
            kwargs.update(**field_args)

        setattr(form_class,
                forward_prop.key,
                self.inline_field_list_type(child_form,
                                            self.session,
                                            info.model,
                                            reverse_prop.key,
                                            info,
                                            **kwargs))

        return form_class

#This is to use a different inline converter, in this case a ForwardInlineModelConverter
class ManyToOneInlineForm(InlineFormAdmin):
    inline_converter = ForwardInlineModelConverter

#This is to use to default inline converter
class OneToManyInlineForm(InlineFormAdmin):
    pass

class PerInlineModelConverterView(ModelView):

    def scaffold_inline_form_models(self, form_class):
        """
            Contribute inline models to the form

            :param form_class:
                Form class
        """
        inline_converter = self.inline_model_form_converter(self.session,
                                                            self,
                                                            self.model_form_converter)

        for m in self.inline_models:
            if hasattr(m, 'inline_converter'):
                custom_converter = m.inline_converter(self.session,
                                                      self,
                                                      self.model_form_converter)

                form_class = custom_converter.contribute(self.model, form_class, m)
            else:
                form_class = inline_converter.contribute(self.model, form_class, m)

        return form_class
        
        
#EXAMPLE

class PackagesView(PerInlineModelConverterView):

    inline_models = ( OneToManyInlineForm(Place), SomeModelUsingDefaultConverter,  ManyToOneInlineForm(Content))
