from django.db.models import F, Func, Value
from myapp.models import MyModel

# Annotation
MyModel.objects.filter(description__icontains='\r\n').annotate(
    fixed_description=Func(
        F('description'),
        Value('\r\n'), Value('\n'),
        function='replace',
    )
)

# Bulk replace/fix
MyModel.objects.filter(description__icontains='\r\n').update(
    description=Func(
        F('description'),
        Value('\r\n'), Value('\n'),
        function='replace',
    )
)
