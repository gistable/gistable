from django.db import models
from django.db.models import signals

class DeletingFileField(models.FileField):
    """
    FileField subclass that deletes the refernced file when the model object
    itself is deleted.
    
    WARNING: Be careful using this class - it can cause data loss! This class
    makes at attempt to see if the file's referenced elsewhere, but it can get
    it wrong in any number of cases.
    """
    def contribute_to_class(self, cls, name):
        super(DeletingFileField, self).contribute_to_class(cls, name)
        signals.post_delete.connect(self.delete_file, sender=cls)
        
    def delete_file(self, instance, sender, **kwargs):
        file = getattr(instance, self.attname)
        # If no other object of this type references the file,
        # and it's not the default value for future objects,
        # delete it from the backend.
        if file and file.name != self.default and \
            not sender._default_manager.filter(**{self.name: file.name}):
                file.delete(save=False)
        elif file:
            # Otherwise, just close the file, so it doesn't tie up resources.
            file.close()
        