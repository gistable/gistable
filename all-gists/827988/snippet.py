from django.template.defaultfilters import slugify
class AutoSlugMixin(object):
    """
    Automatically set slug to slugified version of the name if left empty.
    Use this as follows::

        class MyModel(AutoSlugMixin, models.Model):
            def save(self):
                super(MyModel, self).save()

                self.update_slug()

    The name of the slug field and the field to populate from can be set
    using the `_slug_from` and `_slug_field` properties.

    The big advantage of this method of setting slugs over others
    (ie. django-autoslug) is that we can set the value of slugs
    automatically based on the value of a field of an a field with a foreign
    key relation. For example::

        class MyModel(AutoSlugMixin, models.Model):
            slug = models.SlugField()

            def generate_slug(self):
                qs = self.mymodeltranslation_set.all()[:1]
                if qs.exists():
                    return qs[0].name
                else:
                    return ''

        class MyModelTranslation(models.Model):
            parent = models.ForeignKey(MyModel)
            name = models.CharField()

            def save(self):
                super(MyModel, self).save()

                self.parent.update_slug()

        (The code above is untested and _might_ be buggy.)

    """
    _slug_from = 'name'
    _slug_field = 'slug'

    def slugify(self, name):
        return slugify(name)

    def generate_slug(self):
        name = getattr(self, self._slug_from)
        return self.slugify(name)

    def update_slug(self, commit=True):
        if not getattr(self, self._slug_field) and \
               getattr(self, self._slug_from):
            setattr(self, self._slug_field, self.generate_slug())

            if commit:
                self.save()


class AutoUniqueSlugMixin(AutoSlugMixin):
    """ Make sure that the generated slug is unique. """

    def is_unique_slug(self, slug):
        qs = self.__class__.objects.filter(**{self._slug_field: slug})
        return not qs.exists()

    def generate_slug(self):
        original_slug = super(AutoUniqueSlugMixin, self).generate_slug()
        slug = original_slug

        iteration = 1
        while not self.is_unique_slug(slug):
            slug = "%s-%d" % (original_slug, iteration)
            iteration += 1

        return slug

