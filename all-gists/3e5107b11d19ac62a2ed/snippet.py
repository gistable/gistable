# source: http://stackoverflow.com/questions/1317714/how-can-i-filter-a-date-of-a-datetimefield-in-django

from django.utils import timezone

today_min = datetime.datetime.combine(timezone.now().date(), datetime.time.min)
today_max = datetime.datetime.combine(timezone.now().date(), datetime.time.max)
MyModel.objects.get(date__range=(today_min, today_max))