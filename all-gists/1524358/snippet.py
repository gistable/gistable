
from django import forms
from django.test import RequestFactory

class RangeForm(forms.Form):
    min = forms.IntegerField()
    max = forms.IntegerField()
    valor = forms.IntegerField()

    def clean(self):
        min = self.cleaned_data.get('min')
        max = self.cleaned_data.get('max')
        valor = self.cleaned_data.get('valor')

        if min > max:
            raise forms.ValidationError(u"Limites inválidos")

        if not min <= valor <= max:
            raise forms.ValidationError(u"Valor fora dos limites")

        # obedece o protocolo
        return self.cleaned_data

def simpleview(request):
    "A View"
    form = RangeForm(request.POST)
    if form.is_valid():
        # faça o que vc quiser com o valor
        print form.cleaned_data
    else:
        print form.errors

def post(**kwargs):
    "Helper para simular um post"
    req = RequestFactory().post('/dummy/', kwargs)
    simpleview(req)

# Rodando...
post(min=1, max=10, valor=5)
post(min=6, max=10, valor=5)
post(min=1, max=4, valor=5)
post(min=5, max=10, valor=5)
post(min=1, max=5, valor=5)
post(min=5, max=5, valor=5)
post(min=6, max=5, valor=5)
