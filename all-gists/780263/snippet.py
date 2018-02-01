from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from myapp.models import MyModel


content_type = ContentType.objects.get_for_model(MyModel)

permissions = Permission.objects.filter(content_type=content_type)

# permissions will be a list of Permissions objects

# if you want to get a specific one of the add/change/delete permissions:
permission = Permission.objects.filter(content_type=content_type, codename__startswith='change_')
# replace change_ with add_ or delete_ for the other permissions

# and an alternative method:
perm_name = MyModel._meta.get_add_permission()
perm = Permission.objects.get(codename=perm_name)