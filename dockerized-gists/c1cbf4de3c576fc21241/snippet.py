from functools import partial


def placeholderify(form=None, fields=None):
    """
    A decorator for Django forms that sets a `placeholder` attribute to all
    fields. Each field's label is used as a placeholder.
    
    Use it like so:
    
    @placeholderify
    class MyForm(forms.Form):
        name = forms.CharField(label='Your name')
        email = forms.EmailField(label='Your email')

    Doing that, the `name` field will render like so:
        <input ... placeholder="Your name">
    """
    if form is None:
        return partial(placeholderify, fields=fields)

    class WrappedForm(form):
        def __init__(self, *args, **kwargs):
            super(WrappedForm, self).__init__(*args, **kwargs)

            if fields is None:
                override = self.fields.values()
            else:
                override = [field for name, field in self.fields.items() if name in fields]

            for field in override:
                field.widget.attrs.setdefault('placeholder', field.label)

    return WrappedForm