class SplitDateInput(forms.MultiWidget):
    """
    Виджет для ввода даты с 3 полями.
    """
    def __init__(self, attrs=None):
        widgets = [
            forms.TextInput(attrs=attrs), # день
            forms.Select(attrs=attrs, choices=MONTHS.items()), # месяц
            forms.TextInput(attrs=attrs), # год
        ]
        super(SplitDateInput, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.day, value.month, value.year]
        return [None, None, None]

class SplitDateField(forms.MultiValueField):
    """
    Поля для ввода даты из 3 полей
    """
    widget = SplitDateInput

    def __init__(self, *args, **kwargs):
        fields = (
            forms.IntegerField(min_value=1, max_value=31),
            forms.IntegerField(min_value=1, max_value=12),
            forms.IntegerField(min_value=1900, max_value=2020),
        )
        super(SplitDateField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            day, month, year = data_list
            if not day or not month or not year:
                raise ValidationError(u'Дата - неправильная')
            try:
                result = datetime.date(year, month, day)
            except ValueError:
                raise ValidationError(u'Нет такой даты')
            return result
        return None
