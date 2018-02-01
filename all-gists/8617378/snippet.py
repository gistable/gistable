from django.db import models

class Thing(models.Model):
    # [ snip ]
    def is_deletable(self):
        for rel in self._meta.get_all_related_objects():
            if rel.model.objects.filter(**{rel.field.name: self}).exists():
                return False
        return True