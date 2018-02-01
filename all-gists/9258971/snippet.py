# import signals and slugify
from django.db.models import signals
from django.template.defaultfilters import slugify


# function for use in pre_save
def yourmodel_pre_save(signal, instance, sender, **kwargs):
    if not instance.slug:
        slug = slugify(instance.attribute)  # change the attibute to the field that would be used as a slug
        new_slug = slug
        count = 0
        while YourModel.objects.filter(slug=new_slug).exclude(id=instance.id).count() > 0:
            count += 1
            new_slug = '{slug}-{count}'.format(slug=slug, count=count)
        
        instance.slug = new_slug

# Execute signals pre_save
signals.pre_save.connect(your_model_pre_save, sender=YourModel)
