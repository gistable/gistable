"""
Simple example on how to inject a custom user parameters onto a formset
and its forms.

curry():  https://github.com/django/django/blob/1.4.3/django/utils/functional.py#L9 

Another answer on: 

http://stackoverflow.com/questions/622982/django-passing-custom-form-parameters-to-formset 
"""


class BaseAddToBasketForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.none())
    quantity = forms.IntegerField(initial=0)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user') # user was passed to a single form
        super(BaseAddToBasketForm, self).__init__(*args, **kwargs)


# create a base Formset class
BaseAddToBasketFormSet = formset_factory(BaseAddToBasketForm)   


class AddToBasketFormSet(BaseAddToBasketFormSet): # sub class it

    def __init__(self, *args, **kwargs):
        #  create a user attribute and take it out from kwargs
        # so it doesn't messes up with the other formset kwargs
        self.user = kwargs.pop('user')
        super(AddToBasketFormSet, self).__init__(*args, **kwargs)   

    def _construct_form(self, *args, **kwargs):
        # inject user in each form on the formset
        kwargs['user'] = self.user       
        return super(AddToBasketFormSet, self)._construct_form(*args, **kwargs)



# Instantiate a form for user 'blabla':

AddToBasketFormSet(user="blabla")  