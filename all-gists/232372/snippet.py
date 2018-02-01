class LazyChoiceField(forms.ChoiceField):
    '''
    A Lazy ChoiceField.
    This ChoiceField does not unwind choices until a deepcopy is called on it.
    This allows for dynamic choices generation every time an instance of a Form is created.
    '''
    def __init__(self, *args, **kwargs):
        # remove choices from kwargs.
        # choices should be an iterable
        self._lazy_choices = kwargs.pop('choices',())
        super(LazyChoiceField,self).__init__(*args, **kwargs)
        
    def __deepcopy__(self, memo):
        result = super(LazyChoiceField,self).__deepcopy__(memo)
        lz = self._lazy_choices
        if callable(lz):
            lz = lz()
        result.choices = lz
        return result
