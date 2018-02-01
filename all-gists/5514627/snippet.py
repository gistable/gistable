def validate_count(obj):
    model = obj.__class__
    if model.objects.count() >= 8:
        raise ValidationError('You can add only 8 slider objects %s' % model.__name__)

class Slider(models.Model):
    # Model fields

    def clean(self):
        validate_count(self)