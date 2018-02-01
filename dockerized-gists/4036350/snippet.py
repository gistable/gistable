class BaseClean(object):
    cleaned_data = []
    _errors = []

    def _clean_instance(self):
        for item in dir(self):
            if item.startswith('clean_'):
                validated = getattr(self, item)
                try:
                    if callable(validated):
                        self.cleaned_data.append(validated())
                    else:
                        self.cleaned_data.append(validated)
                except Exception, e:
                    self._errors.append('[%s] %s %s' % (item, type(e), e))

        if hasattr(self, 'clean'):
            validated = getattr(self, 'clean')
            try:
                self.cleaned_data.append(validated())
            except Exception, e:
                self._errors.append('[%s] %s %s' % (item, type(e), e))

    @property
    def errors(self):
        if not self._errors:
            self.full_clean()
        return self._errors

    def full_clean(self):
        self._clean_instance()

    def is_valid(self):
        return not bool(self.errors)


class TestBaseClean(BaseClean):

    @property
    def clean_property(self):
        return 'simple property'

    def clean(self):
        return 'END'

    def clean_test(self):
        return 1 + 1

    def clean_coisa(self):
        return 'coisa'

    def clean_novidade(self):
        return 'Novidade'

    def clean_error(self):
        raise AttributeError('Opa erro')
