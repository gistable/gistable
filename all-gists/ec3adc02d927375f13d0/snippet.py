"""Order a queryset by last_active and make null values sort last."""

import datetime

from django.db.models.functions import Coalesce

from app import models


# Coalesce works by taking the first non-null value.  So we give it
# a date far before any non-null values of last_active.  Then it will
# naturally sort behind instances of Box with a non-null last_active value.
# docs.djangoproject.com/en/1.8/ref/models/database-functions/#coalesce
the_past = datetime.datetime.now() - datetime.timedelta(days=10*365)
boxes = models.Box.objects.all().annotate(
    new_last_active=Coalesce('last_active', Value(the_past))).order_by(
        '-new_last_active')