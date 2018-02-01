def tastypie_template(template_name="base.html", var_name='data', serialize=True):
    """
    Decorator.
    Wrap Tastypie Resource class with it to render into template.

    Usage:

    @tastypie_template()
    class UserResource(ModelResource):
        ...

    @param template_name: template to render
    @param var_name: variable name in template
    @param serialize: serialize data or not
    """
    def outer(original_class):

        def create_response(self, request, data, **kwargs):
            if serialize:
                desired_format = self.determine_format(request)
                data = self.serialize(request, data, desired_format)
            from django.template.response import TemplateResponse
            return TemplateResponse(request, template_name, {var_name: data})

        original_class.create_response = create_response
        return original_class

    return outer