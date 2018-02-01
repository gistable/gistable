from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList

from wagtail.wagtailcore import blocks


class MyLinkBlock(blocks.StructBlock):
    """
    Example validating StructBlock.
    """
    link = blocks.CharBlock(required=False)
    page = blocks.PageChooserBlock(required=False)

    def clean(self, value):
        result = super(MyLinkBlock, self).clean(value)
        errors = {}
        if value['link'] and value['page']:
            errors['link'] = ErrorList([
                'This should not be set when Page is selected',
            ])
        if errors:
            raise ValidationError(
                'Validation error in StructBlock',
                params=errors
            )
        return result
