from django.core.files import File


f = File(open('path_to_file','r'))

m = MyModel.objects.create(one_field='value')

m.file_field = f

m.save()